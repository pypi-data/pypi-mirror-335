from .durable import durable_helper

from .runtime import (
    FaasitRuntime, 
    FaasitResult,
    createFaasitRuntimeMetadata,
    FaasitRuntimeMetadata,
    load_runtime
)
from .utils import (
    get_function_container_config,
    callback,
)
from .workflow import Workflow,Route,RouteBuilder,RouteRunner,WorkflowContext
from typing import Callable, Any
import inspect
from ._private import (
    FunctionConfig,
    LocalFunction,
    AliyunFunction,
    KnativeFunction,
    LocalOnceFunction,
    PKUFunction,
    Function
)

type_Function = Callable[[Any], FaasitResult]

def transformfunction(fn: type_Function) -> type_Function:
    containerConf = get_function_container_config()
    provider = containerConf['provider']
    if provider == 'local':
        def local_function(event,metadata:FaasitRuntimeMetadata = None) -> FaasitResult:
            LocalRuntime = load_runtime('local')
            frt = LocalRuntime(event,metadata)
            return fn(frt)
        return local_function
    elif provider == 'aliyun':
        def aliyun_function(arg0, arg1):
            AliyunRuntime = load_runtime('aliyun')
            frt = AliyunRuntime(arg0, arg1)
            return fn(frt)
        return aliyun_function
    elif provider == 'knative':
        def kn_function(event,metadata: FaasitRuntimeMetadata=None) -> FaasitResult:
            KnativeRuntime = load_runtime('knative')
            frt = KnativeRuntime(event)
            return fn(frt)
        return kn_function
    elif provider == 'aws':
        frt = FaasitRuntime(containerConf)
    elif provider == 'local-once':
        def localonce_function(event, 
                            workflow_runner = None,
                            metadata: FaasitRuntimeMetadata = None
                            ):
            LocalOnceRuntime = load_runtime('local-once')
            if metadata is None:
                metadata = createFaasitRuntimeMetadata(fn.__name__)
            frt = LocalOnceRuntime(event, workflow_runner, metadata)
            result = fn(frt)
            return result
        return localonce_function
    elif provider == 'pku':
        def pku_function(md):
            PKURuntime = load_runtime('pku')
            frt = PKURuntime(createFaasitRuntimeMetadata('stage'),md)
            return fn(frt)
        return pku_function
    else:
        raise ValueError(f"Invalid provider {containerConf['provider']}")

routeBuilder = RouteBuilder()

def durable(fn):
    new_func = durable_helper(fn)
    routeBuilder.func(fn.__name__).set_handler(new_func)
    return new_func


def function(*args, **kwargs) -> Function:

    def __function(fn) -> Function:
        config = get_function_container_config()
        provider = kwargs.get('provider', config['provider'])
        fn_name = kwargs.get('name', fn.__name__)
        cpu = kwargs.get('cpu', 0.5)
        memory = kwargs.get('memory', 128)
        
        func_cls = kwargs.get('wrapper', None)
        Function
        fn_config = FunctionConfig(provider=provider, cpu=cpu, memory=memory, name=fn_name)
        if provider == 'local':
            func = LocalFunction(fn, fn_config)
        elif provider == 'aliyun':
            func = AliyunFunction(fn, fn_config)
        elif provider == 'knative':
            func = KnativeFunction(fn, fn_config)
        elif provider == 'local-once':
            func = LocalOnceFunction(fn, fn_config)
        elif provider == 'pku':
            func = PKUFunction(fn, fn_config)
        else:
            assert(func_cls != None, "wrapper is required for custom runtime")
            assert(issubclass(func_cls, Function), "wrapper must be subclass of Function")
            func = func_cls(fn, fn_config)
        routeBuilder.func(fn_name).set_handler(func.export())
        return func
    if len(args) == 1 and len(kwargs) == 0:
        fn = args[0]
        return __function(fn)
    else:
        return __function
        

def workflow(*args, **kwargs) -> WorkflowContext:
    def __workflow(fn) -> WorkflowContext:
        config = get_function_container_config()
        provider = kwargs.get('provider', config['provider'])
        executor_cls = kwargs.get('executor')
        route = routeBuilder.build()
        def generate_workflow(rt: FaasitRuntime) -> Workflow:
            wf = Workflow(route,fn.__name__)
            if executor_cls != None:
                wf.setExecutor(executor_cls)
            wf.setRuntime(rt)
            r  = fn(wf)
            wf.end_with(r)
            return wf
        routeBuilder.workflow(fn.__name__).set_workflow(generate_workflow)
        return WorkflowContext(generate_workflow, provider, route)

    if len(args) == 1 and len(kwargs) == 0:
        fn = args[0]
        return __workflow(fn)
    else:
        return __workflow


def recursive(fn):
    def Y(f):
        return (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))
    def helper():
        return fn
    return Y(helper)

def create_handler(fn_or_workflow : Function | WorkflowContext):
    container_conf = get_function_container_config()
    if isinstance(fn_or_workflow, WorkflowContext):
        workflow_ctx = fn_or_workflow
        provider = container_conf['provider']
        if provider == 'local':
            async def handler(event:dict, metadata=None):...
                # metadata = createFaasitRuntimeMetadata(container_conf['funcName']) if metadata == None else metadata
                # return await runner.run(event, metadata)
            return handler
        elif provider == 'aliyun':
            def handler(args0, args1):
                if container_conf['funcName'] == '__executor':
                    AliyunRuntime = load_runtime('aliyun')
                    frt = AliyunRuntime(args0, args1)
                    workflow.setRuntime(frt)
                    return workflow.execute(frt.input())
                else:
                    fn = RouteRunner(workflow.route).route(container_conf['funcName'])
                    result = fn(args0,args1)
                    return result
            return handler
        elif provider == 'local-once':
            def handler(event: dict, executor=None):
                result = workflow_ctx.execute(executor)
                return result
            return handler
        elif provider == 'knative':
            from .serverless_function import Metadata
            from .runtime.kn_runtime import KnativeRuntime
            def handler(metadata: Metadata):
                rt = KnativeRuntime(metadata)
                workflow_ctx.set_runtime(rt)
                workflow = workflow_ctx.generate()
                
                return workflow.execute()
        return handler
    else: #type(fn) == Function:
        return fn_or_workflow.export()

    

__all__ = ["_private","workflow","durable","create_handler",'recursive','AbstractFunction']