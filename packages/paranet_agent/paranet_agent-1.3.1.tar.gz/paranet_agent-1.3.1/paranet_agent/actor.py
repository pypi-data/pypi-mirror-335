import copy
import uuid
import inspect
import asyncio
import dataclasses
import typing
import json as json_util
from typing import Optional, Union, get_type_hints
import requests

import strawberry
from strawberry.types.field import StrawberryField
from strawberry.schema.config import StrawberryConfig
from strawberry.aiohttp.views import GraphQLView

from .connector import Server
from .deployment import launch_actors
from .paraflow import PARAFLOW_HOST, use_external_paraflow

# set at launch
prj_name = None


#################### decorators

class SkillField:
    def __init__(self, subject, action, response=False, observe=False, bg=None, skillset=None, instance_param=None):
        self.skillset = skillset
        self.subject = subject
        self.action = action
        self.response = response
        self.observe = observe
        self.bg = bg
        self.instance_param = instance_param


def type(cls = None):
    """Annotates a class as an Paranet data type.  Any class used as an argument in a skill request or returned as a skill
       response must have this annotation.

    This is used before a class declaration:

    ```python
    @actor.type
    class Location:
        lat: float
        lon: float
    ```
    """

    def wrap(cls):
        sb = strawberry.type(cls)
        return sb

    if cls == None:
        return wrap

    return wrap(cls)

def actor(cls = None, *, name=None, subject=None):
    """Annotates a class as an actor.  The classes must extend the `BaseActor` class.

    - `cls` The class (automatic argument when used as a decorator, e.g. @actor.actor).
    - `name` The name of the actor on the Paranet (optional).  If not provided, defaults to the class name in lower case.
    - `subject` The default actor subject (optional).  Skills provided by this actor will have this subject if not specified
      in the `@type.skill`  decorator.  If not provided, the actor subject will be the actor name.

    This is used before a class declaration:

    ```python
    @actor.actor
    class MyActor(BaseActor):
        @actor.skill
        def echo(self, s: str) -> str:
            return s
    ```
    """

    def wrap(cls):
        sb = strawberry.type(cls)
        actor_name = name or cls.__name__.lower()
        def get_name(instance):
            return actor_name
        sb.__actor_name__ = get_name
        sb.__subject__ = subject or actor_name
        return sb

    if cls == None:
        return wrap

    return wrap(cls)

def skill(fn = None, *, id=None, subject=None, action=None, background=None, response=None, instance_param=None):
    """Annotates a method as a skill request handler.

    - `fn` The handler (automatic argument when used as a decorator, e.g. @actor.skill).
    - `subject` The skill subject (optional).  If not provided, defaults to the actor's subject.
    - `action` The skill action (optional).  If not provided, defaults to the name of the method.
    - `background` Indicates that the skill is asynchronous.
    - `response` The response type (implies background).  The type must be a class annotated with `@actor.type`.
    - `instance_param` The instance parameter (optional).  For multi-instance actors, this instance parameter contains an actor instance id.

    This is used inside an actor type declaration:

    ```python
    @actor.actor
    class MyActor(BaseActor):
        @actor.skill
        def echo(self, s: str) -> str:
            return s
    ```
    """

    def wrap(fn):
        sb = strawberry.field(fn)
        bg = True if response != None else background
        sb.__skill__ = SkillField(subject, action or fn.__name__, bg=bg, response=response, skillset=id, instance_param = instance_param)
        return sb

    if fn == None:
        return wrap

    return wrap(fn)

def observation(fn = None, *, subject, action):
    """Annotates a method as a skill observation handler.  This actor does not provide the skill, but merely watches
       requests for the given skill.  The handler is called whenever the skill is observed.  The method parameters must match
       the skill requests inputs.  The method must have a return type None.

    - `fn` The handler (automatic argument when used as a decorator, e.g. @actor.observation).
    - `subject` The observed skill's subject.
    - `action` The The observed skill's action.

    This is used inside an actor type declaration:

    ```python
    @actor.actor
    class MyActor(BaseActor):
        @actor.observation(subject='order',action='new_order')
        def handle_new_order(self, order: Order) -> None:
            ...
    ```
    """

    def wrap(fn):
        sb = strawberry.field(fn)
        sb.__skill__ = SkillField(subject, action or fn.__name__, observe=True)
        return sb

    if fn == None:
        return wrap

    return wrap(fn)

def skill_response(fn = None, *, action=None, subject=None):
    def wrap(fn):
        sb = strawberry.field(fn)
        sb.__skill__ = SkillField(subject, action or fn.__name__, response=True)
        return sb

    if fn == None:
        return wrap

    return wrap(fn)

def skill_request(cls = None, *, subject: str, action: str, response=None):
    def wrap(cls):
        if response:
            if not dataclasses.is_dataclass(response):
                raise Exception('ERROR %s is missing @actor.type class decorator' % (response.__name__,))
  
        dc = dataclasses.dataclass(cls)
        dc.__subject__ = subject
        dc.__action__ = action
        dc.__response__ = response
        dc.__registered__ = False
        return dc

    if cls == None:
        return wrap

    return wrap(cls)

def broadcast(cls = None, *, subject: str=None, action: str):
    def wrap(cls):
        dc = dataclasses.dataclass(cls)
        dc.__subject__ = subject
        dc.__action__ = action
        return dc

    if cls == None:
        return wrap

    return wrap(cls)


#################### globals

noneType = type(None)

actor_registry = {}
actor_instances = {}

pending_requests = {}
pending_responses = {}

def capital_camel(s):
    words = s.split('_')
    return ''.join([w.title() for w in words])

SEND_EVENT = 'send'
COMPLETE_EVENT = 'completed'

def event_api_name(event, actor, subject, action):
    return ''.join([actor, event.title(), capital_camel(subject), capital_camel(action)])

def post_event(prj_name, actor, name, body):
    path_prefix = '/event/' if use_external_paraflow() else '/extern/actors/%s-%s/event/' % (prj_name, actor)
    url = PARAFLOW_HOST + path_prefix + name
    res = requests.post(url, json = body)
    try:
        resp = res.json()
    except:
        print('ERROR event %s failed' % (name,))
        print(res.text)
        raise Exception('Fatal error') from None
    if 'errors' in resp:
        print('ERROR event %s failed' % (name,))
        for e in resp['errors']:
            print('\t'+e)
        raise Exception('Fatal error') from None
    return resp

def handle_skill_response(uid, json):
    if uid in pending_requests:
        inst = pending_requests[uid]
        obj = json_util.loads(json)
        inst.set_response(obj)
        del pending_requests[uid]

def lookup_skill_response(cid):
    if cid in pending_responses:
        resp = pending_responses[cid]
        del pending_responses[cid]
        return resp


#################### Run-time classes

class Conversation:
    """Represents an instance of a skill request"""

    actor: str
    """@private actor name"""

    event: str
    """@private completion event"""

    cid: str
    """Paranet conversation ID"""

    def __init__(self, actor, event, cid):
        """@private constructor"""
        self.actor = actor
        self.event = event        
        self.cid = cid

    def __repr__(self):
        return 'Conversation(%s,%s)' % (self.actor, self.cid)

    def send_complete(self):
        """Send notification of background skill's completion"""
        body = {'cid': self.cid}
        post_event(prj_name, self.actor, self.event, body)

    def send_response(self, data):
        """Send the response from a background skill request"""
        pending_responses[self.cid] = data
        self.send_complete()

class BaseActor:
    """Base class for all actors"""

    def __init__(self):
        pass
    
    def __actor_name__():
        raise Exception('Invalid call on base class')

    def send_request(self, msg):
        """Send a skill request from this actor"""

        cls = msg.__class__
        if not cls.__registered__:
            raise Exception(cls.__name__ + ' skill request not registered in any actor')
        subj = cls.__subject__
        act = cls.__action__
        body = dict(msg.__dict__)
        uid = str(uuid.uuid4())
        body['_uid'] = uid
        pending_requests[uid] = RequestInstance(cls.__response__)
        actor = self.__actor_name__()
        name = event_api_name(SEND_EVENT, actor, subj, act)
        post_event(prj_name, actor, name, body)
        return pending_requests[uid].fut

    def send_broadcast(self, msg):
        """Send a broadcast message from this actor"""

        cls = msg.__class__
        subj = cls.__subject__
        act = cls.__action__
        body = dict(msg.__dict__)
        uid = str(uuid.uuid4())
        body['_uid'] = uid
        actor = self.__actor_name__()
        name = event_api_name(SEND_EVENT, actor, subj, act)
        post_event(prj_name, actor, name, body)

class RequestInstance:
    def __init__(self, resp_cls):
        self.resp_cls = resp_cls
        self.fut = asyncio.get_running_loop().create_future()

    def set_response(self, obj):
        if self.resp_cls:
            data = self.resp_cls(**obj)
            self.fut.set_result(data)
        else:
            self.fut.set_result(None)


#################### GraphQL actor metadata schema

@strawberry.type
class ScalarType:
    name: str

@strawberry.type
class ColumnType:
    name: str
    datatype: str
    optional: bool

@strawberry.type
class TableType:
    columns: list[ColumnType]

@strawberry.type
class SkillArg:
    name: str
    datatype: Union[ScalarType,TableType]
    optional: bool

@strawberry.type
class SkillType:
    subject: str
    action: str
    inputs: list[SkillArg]
    outputs: list[SkillArg]
    event_name: str

@strawberry.type
class Skill:
    subject: str
    action: str
    mutation: str
    response: Optional[str]
    background: Optional[bool]
    observe: Optional[bool]
    skillset: Optional[str]
    event_name: str
    annotations: Optional[list[str]]

@strawberry.type
class Actor:
    name: str
    skills: list[Skill]
    requests: list[SkillType]
    broadcast: list[SkillType]


#################### Builder functions

graphql_typedefs = {}

def get_subject(cls, field):
    return field.__skill__.subject or cls.__subject__

def get_action(field):
    return field.__skill__.action or field.name

def get_field_type(py_type):
    optional = False
    org = typing.get_origin(py_type)
    if org == Union:
        types = typing.get_args(py_type)
        non_null = [t for t in types if t != noneType]
        if len(types) == 2 and len(non_null) == 1:
            # optional type
            py_type = non_null[0]
            optional = True

    if org == list:
        py_type = typing.get_args(py_type)[0]
        hints = get_type_hints(py_type)
        if len(hints) == 0:
            raise Exception('Unsupported list element type: ' + py_type.__name__)
        columns = []
        for name in hints:
            col_type, col_opt = get_field_type(hints[name])
            if isinstance(col_type, ScalarType):
                columns.append(ColumnType(name=name, datatype=col_type.name, optional=col_opt))
            else:
                raise Exception('Unsupported column type in ' + py_type.__name__)
        return (TableType(columns=columns), optional)

    if py_type == int:
        datatype = 'int'
    elif py_type == float:
        datatype = 'double'
    elif py_type == str:
        datatype = 'string'
    else:
        raise Exception('Unsupported type: ' + py_type.__name__)
    return (ScalarType(name=datatype), optional)

def response_query_name(gql_name):
    return 'get%sResponse' % (gql_name.title(),)

# convert py type to Paraflow type
def build_arg(name, py_type):
    datatype, optional = get_field_type(py_type)
    return SkillArg(name=name,datatype=datatype,optional=optional)

def build_arg_list(cls):
    hints = get_type_hints(cls)
    args = []
    for name in hints:
        args.append(build_arg(name, hints[name]))
    return args

def build_request(actor_cls, actor_name, cls):
    if cls.__subject__ == None:
        # update this field so it can be used in send_request
        cls.__subject__ = actor_cls.__subject__
    subj = cls.__subject__
    act = cls.__action__
    inputs = build_arg_list(cls)
    response = cls.__response__
    if response:
        outputs = build_arg_list(response)
    else:
        outputs = []
    event = event_api_name(SEND_EVENT, actor_name, subj, act)
    cls.__registered__ = True
    return SkillType(subject=subj, action=act, inputs=inputs, outputs=outputs, event_name=event)

def build_broadcast(actor_cls, actor_name, cls):
    if cls.__subject__ == None:
        # update this field so it can be used in send_broadcast
        cls.__subject__ = actor_cls.__subject__
    subj = cls.__subject__
    act = cls.__action__
    inputs = build_arg_list(cls)
    cls.__registered__ = True
    event = event_api_name(SEND_EVENT, actor_name, subj, act)
    return SkillType(subject=subj, action=act, inputs=inputs, outputs=[], event_name=event)

def build_skills(cls, actor_name):
    name_converter = StrawberryConfig().name_converter
    fields = [f for f in dataclasses.fields(cls) if isinstance(f, StrawberryField)]
    responses = {}
    for field in fields:
        if field.__skill__.response:
            if inspect.isclass(field.__skill__.response):
                response = response_query_name(name_converter.from_field(field))
            else:
                response = name_converter.from_field(field)
            subj = get_subject(cls, field)
            if subj not in responses:
                responses[subj] = {}
            act = get_action(field)
            responses[subj][act] = response

    skills = []
    for field in fields:
        if not field.__skill__.response or inspect.isclass(field.__skill__.response):
            subj = get_subject(cls, field)
            act = get_action(field)
            bg = field.__skill__.bg
            observe = field.__skill__.observe
            has_response = False
            if subj in responses:
                has_response = act in responses[subj]
            if bg != None and bg:
                if not has_response:
                    print('WARNING: %s/%s completes without a response' % (subj, act))
            else:
                if has_response:
                    raise Exception('ERROR: %s/%s has response method but skill does not have background=True' % (subj,act))
            mutation = name_converter.from_field(field)
            response = None
            if subj in responses:
                if act in responses[subj]:
                    response = responses[subj][act]
            skillset = field.__skill__.skillset
            event = event_api_name(COMPLETE_EVENT, actor_name, subj, act)
            annotations = []
            if field.__skill__.instance_param != None:
                annotations.append(f"%actor_instance(param={field.__skill__.instance_param})")
            skill = Skill(subject=subj,action=act,mutation=mutation,response=response,background=bg,observe=observe,skillset=skillset,event_name=event,annotations=annotations)
            skills.append(skill)
    return skills


def conversation_factory(actor, subject, action, gql_name):
    event = event_api_name('completed', actor, subject, action)
    def hydrate(cid):
        return Conversation(actor, event, cid)

    typename = gql_name.title()+'Conversation'
    if typename in graphql_typedefs:
        scalar = graphql_typedefs[typename]
    else:
        scalar = strawberry.scalar(
            typing.NewType(typename, str),
            serialize=lambda c: c.cid,
            parse_value=hydrate)
        graphql_typedefs[typename] = scalar

    def example(conf: scalar):
        pass

    sb = strawberry.field(example)
    return sb.arguments[0]

def update_conversation_arg(actor, cls, field, gql_name):
    args = list(field.arguments)
    for idx in range(len(args)):
        arg = args[idx]
        if arg.type == Conversation:
            subj = get_subject(cls, field)
            act = get_action(field)
            new_arg = conversation_factory(actor, subj, act, gql_name)
            new_arg.python_name = arg.python_name
            new_arg.graphql_name = '_cid'
            args[idx] = new_arg
            field.arguments = args
            return
    if field.__skill__.bg:
        raise Exception('Skill %s missing Conversation argument' % (field.name,))

def make_response_field(Query, field, gql_name):
    name = response_query_name(gql_name)
    resp_cls = field.__skill__.response
    @strawberry.type
    class Exemplar:
        @strawberry.field(name=name)
        def resolver(cid: str) -> resp_cls:
            return lookup_skill_response(cid)

    fields = [f for f in dataclasses.fields(Exemplar) if isinstance(f, StrawberryField)]
    field = fields[0]
    Query.__annotations__[name] = Exemplar.__annotations__['resolver']
    Query.__dataclass_fields__[name] = field
    Query.__strawberry_definition__.fields.append(field)

def build_query():
    name_converter = StrawberryConfig().name_converter
    actors = list(actor_registry.values())

    @strawberry.type
    class Query:
        @strawberry.field
        def get_actor_metadata() -> list[Actor]:
            return actors

    @strawberry.type
    class Mutation:
        @strawberry.field
        def skill_request_response(uid: str, json: str) -> None:
            handle_skill_response(uid, json)

    for actor_name in actor_instances:
        inst = actor_instances[actor_name]
        cls = inst.__class__
        fields = [f for f in dataclasses.fields(cls) if isinstance(f, StrawberryField)]
        for field0 in fields:
            # need to copy because make_response_field modifies the field
            field = copy.copy(field0)
            field.__skill__ = field0.__skill__

            # replace resolver
            field = field(getattr(inst,field.name).__get__(inst, cls))

            if field.__skill__.response and inspect.isclass(field.__skill__.response):
                make_response_field(Query, field, name_converter.from_field(field))

            if field.__skill__.response and not inspect.isclass(field.__skill__.response):
                Query.__annotations__[field.name] = cls.__annotations__[field.name]
                Query.__dataclass_fields__[field.name] = field
                Query.__strawberry_definition__.fields.append(field)
            else:
                if not field.__skill__.observe:
                    update_conversation_arg(actor_name, cls, field, name_converter.from_field(field))
                Mutation.__annotations__[field.name] = cls.__annotations__[field.name]
                Mutation.__dataclass_fields__[field.name] = field
                Mutation.__strawberry_definition__.fields.append(field)
                
    return Query,Mutation

def register_actor(actor, requests=[], broadcast=[]):
    """Registers an actor for deployment.
    
    - `actor` Instances of an actor class (i.e. class decorated with actor.actor).
    - `requests` List of skill request classes (i.e. classes decorated with actor.type) that define all the skill requests
       this actor makes.
    - `broadcast` List of broadcast classes (i.e. classes decorated with actor.type) that define all the messages this
       actor broadcasts.
    """

    a_cls = actor.__class__
    if not dataclasses.is_dataclass(a_cls):
        raise Exception('ERROR %s is missing @actor.actor class decorator' % (a_cls.__name__,))
    actor_name = actor.__actor_name__()
    skills = build_skills(actor.__class__, actor_name)
    requests = [build_request(a_cls, actor_name, cls) for cls in requests]
    broadcast = [build_broadcast(a_cls, actor_name, cls) for cls in broadcast]
    actor_registry[actor_name] = Actor(name=actor_name, skills=skills, requests=requests, broadcast=broadcast)
    actor_instances[actor_name] = actor

def start_actors(prj, server, restart=True):
    asyncio.ensure_future(launch_actors(prj,list(actor_registry.keys()), server.port, restart))

def _schema_test():
    q,m=build_query()
    schema=strawberry.Schema(query=q,mutation=m)
    print(schema)

    server = Server.get_instance()
    server.set_graphql_view(GraphQLView(schema=schema))

def deploy(prj, restart=True):
    """Deploy all registered actors.  This function will start a docker compose project with one container per actor which
       communications with the Python actors via the connector service

       - `prj` Name of the created docker compose project.
       - `restart` Restart existing containers if already running.
    """

    global prj_name, graphql_typedefs

    graphql_typedefs = {}
    prj_name = prj

    q,m=build_query()
    schema=strawberry.Schema(query=q,mutation=m)
    #print(schema)

    server = Server.get_instance()
    server.set_graphql_view(GraphQLView(schema=schema))

    if not use_external_paraflow():
        start_actors(prj, server, restart)

__all__ = ['Conversation', 'BaseActor', 'actor', 'skill', 'type', 'observation', 'skill_request', 'register_actor', 'deploy']