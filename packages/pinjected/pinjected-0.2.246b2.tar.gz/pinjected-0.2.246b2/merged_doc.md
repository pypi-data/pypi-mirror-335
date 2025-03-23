# Pinjected

Pinjected is a dependency injection / dependency resolver library inspired by [pinject](https://github.com/google/pinject).

This library makes it easy to compose mutliple python objects to create a final object.
When you request for a final object, this library will automatically create all the dependencies and compose them to create the final object.


# Installation
`pip install pinjected`

# Documentations
Please read the following for tutorials and examples.
For more specific api documentation, please look at [documentation](https://pinjected.readthedocs.io/en/latest/)

# Features
- Dependency Injection via Constructor
- Object Dependency Resolution
- Dependency Graph Visualization
- Run configuration creation for intellij idea
- CLI Support
- Functional Depndency Injection Composition

# The Problem
When you write a machine learning code, you often need to create a lot of objects and compose them to create a final object.
For example, you may need to create a model, a dataset, an optimizer, a loss calculator, a trainer, and an evaluator.
You may also need to create a saver and a loader to save and load the model.

Typically these objects creations are controlled by a configuration file like yaml.
A configuration file gets loaded at the top of code and passed to each object creation function.
This make all the codes depend on the configuration file, requiring to have 'cfg' as an argument.
As a result, all the codes heavily depend on the structure of a cfg, and becomes impossible to be used without a cfg object.
This makes it hard to reuse the code, and makes it hard to change the structure of the code too. 
Also, simple testing becomes hard because you need to write a object creation code with its configuration file for each component you want to test.
Moreover, we often see several hundred lines of [configuration parsing code combined with object creation code](https://github.com/CompVis/stable-diffusion/blob/21f890f9da3cfbeaba8e2ac3c425ee9e998d5229/main.py#L418). 
This makes the code hard to read and guess which part is actually doing the work.

# The Solution
Pinjected solves these problem by providing a way to create a final object without passing a configuration object to each object creation function.
Instead, this library will automatically create all the dependencies and compose them to create the final object following the dependency graph.
The only thing you need to do is to define a dependency graph and a way to create each object.
This library will take care of the rest.

This library also provides a way to modify and combine dependency graphs, so that hyperparameter management becomes easy and portable.
By introducing Single Responsibility Principle and Dependency Inversion Principle, the code becomes more modular and reusable.
To this end, this library introduces a concept of Design and Injected object. Design is a collection of object providers with dependencies.
Injected object is an abstraction of object with dependencies, which can be constructed by a Design object.

# Use Case
So, how is that useful to machine learning experiments? Here's an example.

Let's start from a typical machine learning code. (You don't have to understand the code below, please just look at the structure.)

```python
from dataclasses import dataclass

from abc import ABC,abstractmethod
class IoInterface(ABC): # interface for IO used by saver/loader
    @abstractmethod
    def save(self,object,identifier):
        pass
    @abstractmethod
    def load(self,identifier):
        pass
class LocalIo(IoInterface):pass
    # implement save/load locally
class MongoDBIo(IoInterface):pass
    # implement save/load with MongoDB
class Saver(ABC):
    io_interface : IoInterface
    def save(self,model,identifier:str):
        self.io_interface.save(model,identifier)
    
class Loader(ABC):
    io_interface : IoInterface # try to only depend on interface so that actual implementation can be changed later
    def load(self,identifier):
        return self.io_interface.load(identifier)

@dataclass
class Trainer: # try to keep a class as small as possible to keep composability. 
    model:Module
    optimizer:Optimizer
    loss:Callable
    dataset:Dataset
    saver:Saver
    model_identifier:str
    def train(self):
        while True:
            for batch in self.dataset:
                self.optimizer.zero_grad()
                loss = self.loss_calculator(self.model,batch)
                loss.backward()
                self.optimizer.step()
                self.saver.save(self.model,self.model_identifier)
                
@dataclass
class Evaluator:
    dataset:Dataset
    model_identifier:str
    loader:Loader
    def evaluate(self):
        model = self.loader.load(self.model_identifier)
        # do evaluation using loaded model and dataset

```
And configuration parsers:
```python
       
def get_optimizer(cfg:dict,model):
    if cfg['optimizer'] == 'Adam':
        return Adam(lr=cfg['learning_rate'],model.get_parameters())
    elif cfg['optimizer'] == 'SGD':
        return SGD(lr=cfg['learning_rate'],model.get_parameters())
    else:
        raise ValueError("Unknown optimizer")

def get_dataset(cfg:dict):
    if cfg['dataset'] == 'MNIST':
        return MNISTDataset(cfg['batch_size'],cfg['image_w'])
    elif cfg['dataset'] == 'CIFAR10':
        return CIFAR10Dataset(cfg['batch_size'],cfg['image_w'])
    else:
        raise ValueError("Unknown dataset")
    
def get_loss(cfg):
    if cfg['loss'] == 'MSE':
        return MSELoss(lr=cfg['learning_rate'])
    elif cfg['loss'] == 'CrossEntropy':
        return CrossEntropyLoss(lr=cfg['learning_rate'])
    else:
        raise ValueError("Unknown loss")
    
def get_saver(cfg):
    if cfg['saver'] == 'Local':
        return Saver(LocalIo())
    elif cfg['saver'] == 'MongoDB':
        return Saver(MongoDBIo())
    else:
        raise ValueError("Unknown saver")

def get_loader(cfg):
    if cfg['loader'] == 'Local':
        return Loader(LocalIo())
    elif cfg['loader'] == 'MongoDB':
        return Loader(MongoDBIo())
    else:
        raise ValueError("Unknown loader")
def get_model(cfg):
    if cfg['model'] == 'SimpleCNN':
        return SimpleCNN(cfg)
    elif cfg['model'] == 'ResNet':
        return ResNet(cfg)
    else:
        raise ValueError("Unknown model")
    
def get_trainer(cfg):
    model = get_model(cfg),
    return Trainer(
        model=model,
        optimizer = get_optimizer(cfg,model),
        loss = get_loss(cfg),
        dataset = get_dataset(cfg),
        saver = get_saver(cfg),
        model_identifier = cfg['model_identifier']
    )

def get_evaluator(cfg):
    return Evaluator(
        dataset = get_dataset(cfg),
        model_identifier = cfg['model_identifier'],
        loader = get_loader(cfg)
    )

def build_parser():
    """
    very long argparse code which needs to be modified everytime configuration structure changes
    """

if __name__ == "__main__":
    # can be argparse or config.json
    # cfg:dict = json.loads(Path("config.json").read_text())
    # cfg = build_parser().parse_args()
    cfg = dict(
        optimizer = 'Adam',
        learning_rate = 0.001,
        dataset = 'MNIST',
        batch_size = 128,
        image_w = 256,
        loss = 'MSE',
        saver = 'Local',
        loader = 'Local',
        model = 'SimpleCNN',
        model_identifier = 'model1'
    )
    trainer = get_trainer(cfg)
    trainer.train()
```
This code first loads a configuration via file or argparse.
(Here the cfg is constructed manually for simplicity.)

Then it creates all the objects and composes them to create a final object using a cfg object.
The problem we see are as follows:

1. Config Dependency:
   - All the objects depend on the cfg object, which makes it hard to reuse the code. 
   - The cfg object will get referenced deep inside the code, such as a pytorch module or logging module.
   - The cfg object often gets referenced not only in the constructor, but also in the method to change the behavior of the object.
2. Complicated Parser: 
   - The parser for config object gets quite long and complicated as you add more functionalities 
   - We see a lot of nested if-else statements in the code.
   - It is impossible to track the actual code block that is going to run due to nested if-else statements.
3. Manual Dependency Construction: 
   - The object dependency must be constructed manually and care must be taken to consider which object needs to be created first and passed.
   - When the dependency of an object changes, the object creation code must be modified. 
     - (suppose the new loss function suddenly wants to use the hyperparameter of the model, you have to pass the model to get_model() function!)
     

Instead, we can use Pinjected to solve these problems as follows:
```python
from dataclasses import dataclass
from pinjected import instances,providers,injected,instance,classes

@instance
def optimizer__adam(learning_rate,model):
    return Adam(lr=learning_rate,model.get_parameters())
@instance
def dataset__mydataset(batch_size,image_w):
    return MyDataset(batch_size,image_w)
@instance
def model__sequential():
    return Sequential()
@instance
def loss__myloss():
    return MyLoss()

conf:Design = instances(
    learning_rate = 0.001,
    batch_size = 128,
    image_w = 256,
) + providers(
    optimizer = optimizer__adam,
    dataset = dataset__mydataset,
    model = model__sequential,
    loss = loss__myloss
) + classes(
    io_interface = LocalIo# use local file system by default
)

g = conf.to_graph()
#lets see model structure
print(g['model'])
# now lets do training
g[Trainer].train()
# lets evaluate
g[Evaluator].evaluate()
```
Let's see how the code above solves the problems we mentioned earlier.
1. Config Dependency: 
   - All the objects are created without depending on the cfg object.
   - Design object serves as a configuration for constructing the final object.
   - Each object is only depending on what the object needs, not the whole configuration object.
   - Each object can be tested with minimum configuration.
     - For example, dataset object can be tested with only batch_size and image_w.
2. Complicated Parser:
   - The parser is replaced with a simple function definition.
   - The function definition is simple and easy to understand.
   - The actual code block that is going to run is clear. 
   - No nested if-else statements.
   - No string parsing to actual implementation. Just pass the implementation object.
3. Manual Dependency Construction -> Automatic Dependency Construction:
   - The object dependency is constructed automatically by Pinjected.
   - The object dependency is resolved automatically by Pinjected.
   - When the dependency of an object changes, the object creation code does not need to be modified.
     - (suppose the myloss function suddenly wants to use the hyperparameter of the model, you only need to change the signature of loss__myloss to accept model/hyperparameter as an argument.)
```python
#Example of changing the loss function to use model hyperparameter
@instance
def loss_myloss2(model):
    return MyLoss(model.n_embeddings)
```

This doesnt look useful if you have only one set of configuration,
but when you start playing with many configurations,
this approach really helps like this.

```python
conf = instances(
    learning_rate = 0.001,
    batch_size = 128,
    image_w = 256,
) + providers(
    optimizer = provide_optimizer,
    dataset = provide_dataset,
    model = provide_model,
    loss_calculator = provide_loss_calculator
) + classes(
    io_interface = LocalIo# use local file system by default
)


conf_lr_001 = conf + instances(# lets change lr
    learning_rate=0.01
)
conf_lr_01 = conf + instances(
    learning_rate=0.1
)
lstm_model = providers( # lets try LSTM?
    model = lambda:LSTM()
)
save_at_mongo = classes( # lets save at mongodb
    io_interface = MongoDBIo
)
conf_lr_001_lstm = conf_lr_001 + lstm_model # you can combine two Design!
conf_lr_01_mongo = conf_lr_01 + save_at_mongo
for c in [conf,conf_lr_001,conf_lr_01,conf_lr_001_lstm,conf_lr_01_mongo]:
    g = c.to_graph()
    g[Trainer].train()
```
The good thing is that you can keep old configurations as variables.
And modifications on Design will not break old experiments.
Use this Design and keep classess as small as possible by obeying the Single Resposibility Principle.
Doing so should prevent you from rewriting and breaking code when implmenting new feature.
## Adding Feature Without Rewriting
If you come up with a mind to extremely change the training procedure without breaking old experiments, you can create a new class and bind it as a "trainer".
Suppose you come up with a brilliant new idea that making the model play atari_game during training might help training like so:
```python
class AtariTrainer:
    model:Module
    optimizer:Optimizer
    dataset:Dataset
    atari_game:AtariGame
    loss_calculator:Callable
    def train(self):
        for batch in self.dataset:
            # lets play atari_game so that model may learn something from it.
            self.optimizer.zero_grad()
            self.atari_game.play(self.model)
            loss = self.loss_calculator(self.model,batch)
            self.optimizer.step()
            # do anything
my_new_training_strategy = classes(
    trainer=AtariTrainer
)
conf_extreme=conf_lr_01_mongo + my_new_training_strategy
g = conf_extreme.to_graph()
g["trainer"].train()# note the argument to 'provide' method can be a type object or a string.
```
as you can see, now you can do training with new AtariTrainer without modifying the existing code at all.
Furthermore, the old configurations are still completely valid to be used.
If you dont like the fact some code pieces are repeated from original Trainer, you can introduce an abstraction for that using generator or reactive x or callback.

[Next: Design](02_design.md)

# Design in Pinjected
The Design class is a fundamental concept in Pinjected that allows you to define and compose dependency injection configurations. It provides a flexible way to specify bindings for objects and their dependencies.
Adding Bindings
You can create a Design by combining different types of bindings:
```python 
from pinjected import instances, providers, classes, design
from dataclasses import dataclass


@dataclass
class DepObject:
    a: int
    b: int
    c: int
    d: int


@dataclass
class App:
    dep: DepObject
    def run(self):
        print(self.dep.a + self.dep.b + self.dep.c + self.dep.d)


d = instances(
    a=0,
    b=1
) + providers(
    c=lambda a, b: a + b,
    d=lambda a, b, c: a + b + c
) + classes(
    dep=DepObject
)
d2 = design( # same definition as the d. This automatically switches instances/providers/classes depending on the type of the object
    a=0,
    b=1,
    c=lambda a, b: a + b,
    d=lambda a, b, c: a + b + c,
    dep=DepObject
)
```
In this example, we create a Design by combining:

- instances(): Binds concrete values
- providers(): Binds functions that provide values
- classes(): Binds classes to be instantiated
- design(): Automatically switches instances/providers/classes depending on the type of the object
  - If the object is a class, it is bound as a class
  - If the object is a callable, it is bound as a provider
  - If the object is an object that is not callable (i.e,, no __call__ method), it is bound as an instance
  
## Resolving Dependencies
To resolve dependencies and create objects based on a Design, you can use the to_graph() method.
It returns an object graph that allows you to access the resolved objects. 
```python
g = d.to_graph()
app = g['app']
```
The graph resolves all the dependencies recursively when ['app'] is required.
Note that the graph instantiates objects lazily, meaning that objects are created only when they are needed.

# instances()

instances() is a function to create a Design with constant values. 
The value is bound to the key, and its value is directly used when the key is required.

# providers()
providers() is a function to create a Design with providers.
A provider functions bound with this function are meant to be invoked lazily when the value is needed.

A provider is one of the following types: a `callable`, an `Injected` and an `IProxy`. 
## `callable`:
A callable can be used as a provider. 
When a callable is set as a provider, its argument names are used as the key for resolving dependencies.
```python
from pinjected import providers, instances
d = providers(
    a=lambda: 1,
    b=lambda a: a + 1 # b is dependent on a
)
g = d.to_graph()
assert g['a'] == 1
assert g['b'] == 2 
```

## `Injected`
An Injected can be used as a provider. Injected is a python object that represents a variable that requires injection.
When an Injected is set as a provider, it is resolved by the DI.
```python
from pinjected import providers, instances, Injected
d = instances(
    a = 1
)+providers(
    b=Injected.bind(lambda a: a+1)
)
g = d.to_graph()
assert g['b'] == 2
```
Please read more about Injected in the [Injected section](docs_md/04_injected.md).

## `IProxy`
An IProxy can be used as a provider. 
When an IProxy is set as a provider, it is resolved by the DI.
```python
from pinjected import providers, instances, injected, IProxy


@injected
def b(a: int, /):
    return a + 1


b: IProxy
d = instances(
    a=1
) + providers(
    b=b
)
g = d.to_graph()
assert g['b'] == 2

```
When `@injected` or `@instance` is used, the decorated function becomes an instance of IProxy.
IProxy can be composed with other IProxy or Injected to create a new IProxy easily.

Please refer to the [IProxy section](docs_md/04_injected_proxy) for more information.

# `classes`
classes() is a function to create a Design with classes. However, currently the implementation is completely the same as providers().
A class is a callable and can be used as a provider. 

[Next: Injected](03_decorators.md)




## @instance and @injected Decorators

Pinjected provides two decorators for defining provider functions: `@injected` and `@instance`. While both decorators are used to create objects within the dependency injection framework, they have distinct behaviors and use cases.

### @instance
The @instance decorator is used to define a provider function that takes only injected arguments. All the arguments are considered injected and will be resolved by Pinjected.

When using @instance, Pinjected will resolve them based on the dependency graph. The decorated function will directly return the created object, without requiring any further invocation.

Note: Objects created with @instance are singleton-like within the same object graph (g). This means that for a given set of injected arguments, the @instance decorated function will be called only once, and the same instance will be reused for subsequent requests within the same g.

Here's an example:

```python
@instance
def train_dataset(logger, train_cfg):
    logger.info(f"Creating train_dataset with {train_cfg.dataset}. This is only called once.")
    # note a logger can be injected as well
    return get_dataset(train_cfg.dataset)


@instance
def logger():
    from pinjected.pinjected_logging import logger
    return logger


# Usage
design: Design = instances(
    train_cfg=dict(dataset='dummy')
) + providers(
    logger=logger
)

g = design.to_graph()
dataset_1 = g['train_dataset']  # dataset is only created once for a g.
dataset_2 = g['train_dataset']  # the same dataset is returned
assert id(dataset_1) == id(dataset_2), "dataset_1 and dataset_2 should be the same object"
assert id(g['train_cfg']) == id(g['train_cfg']), "train_cfg should be the same object"
```

### @injected

The `@injected` decorator is used to define a provider function that takes both injected and non-injected arguments. 
It allows you to create a function that require some dependencies to be resolved by Pinjected,
while also accepting additional arguments that need to be provided explicitly.
In other words, '@injected' allows you to provide a function instead of a value.

When using `@injected`, you separate the injected and non-injected arguments using the `/` symbol. The arguments before the `/` are considered injected and will be resolved by Pinjected based on the dependency graph. The arguments after the `/` are non-injected and need to be provided when invoking the returned function.

Here's an example:

```python
@injected
def train_loader(train_dataset, train_cfg, /, batch_size):
  return DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=train_cfg.num_workers,
                    drop_last=train_cfg.drop_last)

@injected
def trainer(model, train_loader, /, epochs):
  train_loader:Callable[[int],DataLoader] # here train_loader is a function that only takes 'batch_size'.
  for epoch in range(epochs):
    for batch in train_loader(batch_size=32):
      # Training loop
      ...

# Usage
design = providers(
  train_dataset=train_dataset,
  train_cfg=train_cfg,
  model=model,
)

trainer_fn:Callable[[int],None] = design.provide(trainer)
# Now you can call the trainer_fn with the non-injected argument 'epochs'
trainer_fn(epochs=10)
```

In this example, train_dataset, train_cfg, and model are injected arguments, 
while batch_size and epochs are non-injected arguments. 
The trainer function takes model and train_loader as injected arguments, and epochs as a non-injected argument.

Note that the name of the decorated function train_loader is implicitly added to the design, 
allowing it to be used as an injected argument in the trainer function.
Inside the trainer function, train_loader is invoked with the non-injected argument batch_size to obtain the actual data loader instance. 
The training loop then uses the data loader to iterate over the batches and perform the training process.

To use the trainer function, you create a Design object and bind the necessary instances (train_dataset, train_cfg, and model). 
Then, you can call design.provide(trainer) to obtain the trainer_fn function. 
Finally, you invoke trainer_fn with the non-injected argument epochs to start the training process.

### Choosing Between @injected and @instance
The choice between @injected and @instance depends on your specific use case and the nature of the provider function.

Use @injected when you have a provider function that requires both injected and non-injected arguments. It provides flexibility to accept additional arguments that are not part of the dependency graph.
Use @instance when you have a simple provider function that only depends on injected arguments. It is a more concise way to define provider functions that don't require any additional invocation.
By leveraging these decorators appropriately, you can define provider functions that align with your dependency injection needs and create objects with the desired level of flexibility and simplicity.

[Next: Injected](04_injected.md)
# class Injected

`Injected` is a python object that represents a variable that requires injection.
It has a set of dependencies that are required to be created, and a provider function that creates the variable.

```python
from pinjected.di.util import Injected
import asyncio
from pinjected import instances


def provide_ab(a: int, b: int):
    return a + b


# Injected.bind can convert a provider function to an Injected object.
# the names of arguments are used as dependencies.
injected: Injected[int] = Injected.bind(provide_ab)
design = instances(
    a=1,
    b=2
)
assert design.to_graph()[injected] == 3
assert injected.dependencies() == {'a', 'b'}
assert asyncio.run(injected.get_provider()(a=1, b=2)) == 3
# Injected's provider is automatically async for now.
```

## Injected composition

### map

You can map an Injected to create another injected instance.
Similar to the map function in functional programming, the value of the Injected is transformed by the function.
```python
from pinjected.di.util import Injected, instances
from pinjected import Design

design: Design = instances(
    a=1,
)
a: Injected[int] = Injected.by_name('a')
# by_name is a helper function to create an Injected instance that depends on the given name, and returns its value on resolution.
b: Injected[int] = a.map(lambda x: x + 1)  # must be a + 1
g = design.to_graph()
assert g[a] == 1  # by_name just returns the value of the key.
assert g[a] + 1 == g[b]
```

### zip/mzip

You can combine multiple injected instances into one.
The dependencies of the new Injected will be the union of the dependencies of the original Injected.

```python
from pinjected.di.util import Injected
from pinjected import Design


def provide_ab(a: int, b: int):
    return a + b


design = instances(
    a=1,
    b=2
)
g = design.to_graph()
# you can use getitem to get the value of Injected by key
assert g['a'] == 1
assert g['b'] == 2
a = Injected.by_name('a')
b = Injected.by_name('b')
c = a.map(lambda x: x + 2)
abc = Injected.mzip(a, b, c)
ab_zip = Injected.zip(a, b)  # use mzip if you need more than 2 Injected
assert g[abc] == (1, 2, 3)
assert g[ab_zip] == (1, 2)
```

### dict/list

since we have map and zip, we can create dict and list from pinjected.

```python
from pinjected.di.util import Injected, instances

design = instances(
    a=1,
    b=2
)
a = Injected.by_name('a')
b = Injected.by_name('b')
c = a.map(lambda x: x + 2)
injected_dict: Injected[dict] = Injected.dict(a=a, b=b, c=c)  # == {'a':1,'b':2,'c':3}
injected_list: Injected[list] = Injected.list(a, b, c)  # == [1,2,3]
```

## Partial Injection

Now the fun part begins. we can partially inject a function to receive some of its arguments from DI.
This turns a Callable into Injected[Callable].
The separation between the arguments meant to be injected and the arguments that are not meant to be injected is
done by a `/` in the argument list. So all the positional-only arguments become the dependencies of the Injected.

```python
from pinjected.di.util import Injected, instances
from pinjected import injected,IProxy
from typing import Callable


@injected
def add(a: int, b: int, /, c: int):
    # a and b before / gets injected.
    # c must be provided when calling the function.
    return a + b + c


design = instances(
    a=1,
    b=2,
)
add_func: IProxy[Callable[[int], int]] = add
total: IProxy[int] = add(c=3)  # can be add_func(c=3) or add_func(3) or add(3)
g = design.to_graph()
assert g[total] == 6
assert g[add(3)] == 6
assert g[add](3) == 6
```

## Constructing a tree of injected

We can also form a syntax tree of injected functions, to create another injected instance.

```python
from pinjected.di.util import Injected, instances
from pinjected import injected
from typing import Callable


@injected
def x(logger, /, a: int):
    logger.info("x called")
    return a + 1


@injected
def y(logger, database_connection, /, x: int):
    logger.info(f"y called with x, using {database_connection}")
    return x + 1


x_andthen_y: Injected[int] = y(x(0))
design = instances(
    logger=print,
    database_connection="dummy_connection"
)
g = design.to_graph()
assert g[x_andthen_y] == 2
assert g[y(x(0))] == 2
```

This means that we can chain as many injected functions as we want, and the dependencies will be resolved automatically.

## Using Injected as a provider

Injected can be used as a provider function in a design.

```python
from pinjected.di.util import Injected, instances, providers, Design
from pinjected import injected, instance


@instance
def d_plus_one(d):
    return d + 1


# you can use instance as decorator when you don't need any non_injected arguments.
# now get_d_plus_one is Injected[int], so an integer will be created when it is injected by DI.
# don't forgeet to add slash in the argument list, or the arguments will not be injected.
@injected
def calc_d_plus_one(d: int, /, ):
    return d + 1


# you can use injected as decorator when you need non_injected arguments.
# if you don't provide non_injected arguments, it will a injected function that does not take any arguments when injected.
# now get_d_plus_one is Injected[Callable[[],int]], so a callable will be created when it is injected by DI.

d = instances(
    a=1,
    b=2
) + providers(
    c=lambda a, b: a + b,
    d=Injected.by_name('a').map(lambda x: x + 1),
    e=d_plus_one,
    get_e=calc_d_plus_one,
)
g = d.to_graph()
g['d'] == 2
g['e'] == 3
g['get_e']() == 4  # get_e ends up as a callable.
```

## Overriding Provider Function with Injected

Suppose you have a provider function already as follows:

```python
def provide_c(a,
              b):  # you dont have to prefix this function name with "provide", but I suggest you use some naming convention to find this provider later on.
    return a + " " + b


d = instances(
    a="my",
    b="world"
) + providers(
    c=provide_c
)
```

but you want to override the provider function to use a specific value rather than a value from DI.
You can do as follows:

```python
from pinjected.di.util import Injected

overriden: Injected = Injected.bind(provide_c, a=Injected.pure("hello"))
d2 = d + providers(
    c=overriden
)
d.provide("c") == "my world"
d2.provide("c") == "hello world"
```

so that "a" can be manually injected only for "c".
Injected.bind takes a function and kwargs. kwargs will be used for overriding the parameter of given function.
Overriding value must be an instance of Injected. For pure instance, use Injected.pure. If you want to give a provider
function to be used for the function, use Injected.bind.

```python
injected_c = Injected.bind(provide_c,
                           a=Injected.bind(lambda b: b + "nested"),  # you can nest injected
                           b="a"  # this will make dependency named 'a' to be injected as 'b' for provide_c.
                           )  # you can nest Injected
```


[Next: IProxy](04_injected_proxy.md)
# IProxy

IProxy is a class to help easy programming with Injected objects. 
This class provides a direct way of composing multiple Injected objects and calling a Injected function to get a new IProxy object.
Essentially, IProxy is a proxy object for an Injected object to construct an AST to be parsed by the Design later.

## How to make an IProxy object
1. Use the `@instance` decorator to create an IProxy object.
```python
@instance
def test_value(dep):
    return "hello"

test_value:IProxy[str]
```

2. Use the `@injected` decorator to create an IProxy object.
```python
@instance
def test_func(dep,/,x:int):
    return x + 1

test_func:IProxy[Callable[[int],int]]
```

3. Use the .proxy attribute on Injected object
```python
test_inject:Injected[str] = Injected.pure('test')
test_proxy:IProxy[str] = test_inject.proxy
```

## How to use IProxy object
Identical to Injected object, IProxy object can be used with Design class.
```python
from pinjected import providers,IProxy,Injected
d = providers(
    x = Injected.pure('hello').proxy # same as passing Injected.pure('hello')
)

x_proxy:IProxy[str] = Injected.by_name('x').proxy

g = d.to_graph()
assert g['x'] == 'hello'
assert g[x_proxy] == 'hello' # proxy can be passed to g's __getitem__ method
```

## IProxy Composition
IProxy is a class to provide easy composition of Injected objects and functions without using tedeous 'map' and 'zip' functions.

Let's begin from the simple map/zip example.
```python
from pinjected import providers,IProxy,Injected

x = Injected.pure(1)
x_plus_one = x.map(lambda x: x + 1)

assert providers()[x_plus_one] == 2, "x_plus_one should be 2"
```
Now, with IProxy, this can be re-written as:
```python
from pinjected import providers,IProxy,Injected
x = Injected.pure(1).proxy
x_plus_one = x + 1
assert providers()[x_plus_one] == 2, "x_plus_one should be 2"
```
This is achieved by overridding the __add__ method of IProxy to create a new IProxy object.
We have implemented most of the magic methods to make this work, so we can do things like:
```python
from pinjected import instances,IProxy,Injected
from pathlib import Path
fun = lambda x: x + 1

fun_proxy:IProxy[Callable[[int],int]] = Injected.pure(fun).proxy
call_res:IProxy[int] = fun_proxy(1)
call_res_plus_one:IProxy[int] = fun_proxy(1) + 1
anything:IProxy[int] = (fun_proxy(1) + fun_proxy(2)) / 2
cache_dir:IProxy[Path] = Injected.by_name("cache_dir").proxy
cache_subdir:IProxy[Path] = cache_dir / "subdir"

list_proxy:IProxy[list[int]] = Injected.pure([0,1,2]).proxy
list_item:IProxy[int] = list_proxy[1]


g = instances(
    cache_dir=Path("/tmp")
).to_graph()

assert g[cache_subdir] == Path("/tmp/subdir"), "cache_subdir should be /tmp/subdir"
assert g[list_item] == 1, "list_item should be 1"
```

[Next: Running](./05_running.md)

# CLI Support

An Injected instance can be run from CLI with the following command.

```bash
python -m pinjected run [path of an Injected variable] [optional path of a Design variable] [Optional overrides for a design] --additional-bindings
```

- Variable Path: `your.package.var.name`
- Design Path: `your.package.design.name`
- Optional Overrides: `your.package.override_design.name`

## Example CLI Calls

```bash
python -m pinjected my.package.instance --name hello --yourconfig anystring
```

This CLI will parse any additional keyword arguments into a call of `instances` internally to be appended to the design
running this injected instance.
Which is equivalent to running following script:

```python
from my.package import instance
design = instances(
    name='dummy',
    yourconfig='dummy'
) + instances(
    name = 'hello',
    yourconfig = 'anystring'
)

design.provide(instance)
```

### Using Injected variable in CLI argument
We can use `{package.var.name}` to tell the cli that the additional bindings are to be imported from the specified path.

Example:

```python
# my.module2.py
from pinjected import instance
@instance
def load_hostname():
    import socket
    return socket.gethostname()
```

```python
# my.module.py
from pinjected import injected


@injected
def print_hostname(hostname):
    print(hostname)
```

```bash
python -m pinjected run my.module.print_hostname --hostname "{my.module2.load_hostname}"
```

This is useful for switching complicated injected instances for running the target. The complicated injected instances
can be trained ML models, etc.

Example2:

```python
# some.llm.module.py
from pinjected import injected


@injected
def llm_openai(openai_api_key, /, prompt):
    return "call open ai api with prompt..."


@injected
def llm_azure(azure_api_key, /, prompt):
    return "call azure api with prompt..."


@injected
def llm_llama(llama_model_on_gpu, configs, /, prompt):
    return llama_model_on_gpu(prompt, configs)


@injected
def chat(llm, /, prompt):
    return llm(prompt)
```

```bash
python -m pinjected run some.llm.module.chat --llm="{some.llm.module.llm_openai}" "hello!"
```

Now we can switch llm with llm_openai, llm_azure, llm_llama... by specifying a importable variable path.

## __meta_design__

`pinjected run` reads `__meta_design__` variables in every parent package of the target variable:

```
- some_package
  | __init__.py   [-- can contain __meta_design__
  | module1
  | | __init__.py [-- can contain __meta_design__
  | | util.py     [-- can contain __meta_design__
```

When running "python -m pinjected run some_package.module1.util.run", all "__meta_design__" in parent packages will be loaded and concatenated. 
Which in this case results in equivalent to running the following script:

```python
meta_design = some_package.__meta_design__ + some_package.module1.__meta_design + some_package.module1.util.__meta_design__
overrides = meta_design.provide('overrides')
default_design = import_if_exist(meta_design['default_design_path'])
g = (default_design + overrides).to_graph()
g[some_package.module1.util.run]
```


## .pinjected.py

Additionaly, we can place .pinjected.py file in the current directly or the home directory. a global variable named '
default_design' and 'overrides' will be automatically imported, then prepended and appended to the design before running
the target.

This is convinient for specifying user specific injection variables such as api keys, or some user specific functions.



# AsyncIO support
pinjected supports using async functions as a provider. For async providers, each dependencies are gathered in parallel, and the provider function is called in an async context.
```python
from pinjected import instances, providers, injected, instance
import asyncio


@instance
async def x():
    await asyncio.sleep(1)
    return 1


@injected
async def y_provider(x, /):
    # Note that we do not need to await x, because it is already awaited by the DI.
    await asyncio.sleep(1)
    return x + 1


@injected
async def y_user(y):
    # Here, we need to await y since injected y is an async function.
    return await y()


@instance
def non_async_x():
    # we can also combine non-async and async functions.
    return 1


d = providers(
    x=x,
    y=y_provider
)
g = d.to_graph()  # to_graph returns a blocking resolver that internally call asyncio.run to resolve the dependencies.
assert g['y'] == 2
async_g = d.to_resolver()  # to_resolver returns an async resolver that can be awaited.
assert (await async_g['y']) == 2
```

## AsyncIO support for Injected AST composition
```python
from pinjected import instances, providers, injected, instance
import asyncio


@instance
async def x():
    await asyncio.sleep(1)
    return 1


@instance
def alpha():
    return 1


@injected
async def slow_add_1(x, /):
    await asyncio.sleep(1)
    return x + 1


# we can construct an AST of async Injected instances.
y = slow_add_1(x)
# we can also combine non-async and async Injected variables 
z = y + alpha

d = providers()
g = d.resolver()

assert (await g[y]) == 2
assert (await g[z]) == 3


```



# Object Graph
Our `Design.to_graph()` creates an object graph. This object graph controlls all the lifecycle of injected variables.
Calling `g.provide("something")` asks the graph if "something" is already instantiated in the graph and retrieves it.
If "something" was not instantiated, then "something" is instantiated along with its dependencies.

# Calling `provide` directly from Design
This will create a temporary short-lived object graph just for this `provide` call and returns its injection result.
Use this for debugging or factory purposes.
If you bind a function that returns a random value as a binding, calling the same Graph's `provide` should always
return the same value, while Design's `provide` should return a random value for each invocation.
```python
import random
d = providers(
    r = lambda : random.uniform(0,1)
)
g = d.to_graph()
g.provide("r") == g.provide("r")
d.provide("r") != d.provide("r")# it is random. should rarely be the same.
```


# Config Creator for Intellij Idea

Through `__meta_design__`, a custom run config creator can be created for Intellij Idea. This is useful for running the
target with different injected instances.

We introduce a IRunner interface that can be used to run arbitrary shell command on a target.
For example, we can implement a runner for GCE, AWS, Local, or Docker.

```python
class IRunner:
    async def run(self, cmd: str) -> str:
        pass

# an example of a local runner:
class LocalRunner(IRunner):
    async def run(self, cmd: str) -> str:
        import subprocess
        return subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
```

We call this runner an environment, to run a command.

Now, we can use this env to automatically add a run configuration for an injected object to be run on the target
environment.

This means that we can run any `injected` object on chosen environment.

To do so, we need to add a config creator to `__meta_design__` with `idea_config_craetor_from_envs` function.

```python
# assume this is some_module.py
from pinjected import *

local_env = injected(LocalRunner)()

__meta_design__ = providers(
    custom_idea_config_craetor=idea_config_craetor_from_envs(
        [
            "some_module.local_env"
        ]
    )
)
```

Now, with pinjected plugin installed on intellij or vscode, you can click on the green triangle on the left of an `injected`
variable,
and then select an environment `local_env` to run it.

By implementing IRunner for any environment of your choice,
You can quickly switch the target environment for running the injected object.



# Visualization (Supported after 0.1.128)
Pinjected supports visualization of dependency graph.
```bash
pinjected run_injected visualize <full.path.of.Injected.variable> <full.path.of.Design.variable>
```
For example:
```bash
pinjected run_injected visualize pinjected.test_package.child.module1.test_viz_target pinjected.test_package.child.module1.viz_target_design
```

# Picklability
Compatible with dill and cloudpickle as long as the bound objects are picklable.


# IDE-support
A plugin exists for IntelliJ Idea to run Injected variables directly from the IDE.

Requirements:
- IntelliJ Idea
- __meta_design__ variable declaration in a python file.

### 1. Install the plugin to IntelliJ Idea/PyCharm
### 2. open a python file.
Write a pinjected script, for example:
```python
# test_package.test.py
from pinjected import instances, Injected, injected, instance


@instance
async def test_variable():
  """
  this test_vaariable can now directly be run from IntelliJ Idea, by clicking the Run button associated with this line.
  a green triangle will appear on the left side of the function definition.
  """
  return 1

from returns.maybe import Some, Nothing
__meta_design__ = instances(
    default_design_path='test_package.design',
    default_working_dir=Some("/home/user/test_repo"), # use Some() to override, and Nothing to infer from the project structure.
)
```

Now, you can run the `test_variable` by clicking the green triangle on the left side of the function definition.

## Customizing the Injected variable run
To add additional run configurations to appear on the Run button, you can add a bindings to __meta_design__.
The plugin picks up a 'custom_idea_config_creator' binding and use it for menu item creation.

```python
from typing import List, Callable

CustomIdeaConfigCreator = Callable[[ModuleVarSpec], List[IdeaRunConfiguration]]


@injected
def add_custom_run_configurations(
        interpreter_path:str,
        default_working_dir,
        /,
        cxt: ModuleVarSpec) -> List[IdeaRunConfiguration]:
    return [IdeaRunConfiguration(
        name="HelloWorld",
        script_path="~/test_repo/test_script.py",
        interpreter_path=interpreter_path,# or your specific python's path, "/usr/bin/python3",
        arguments=["--hello", "world"],
        working_dir="~/test_repo", # you can use default_working_dir
    )]

__meta_design__ = instances(
    custom_idea_config_creator=add_custom_run_configurations
)

```

You can use interpreter_path and default_working_dir  as dependencies, which are automatically injected by the plugin.
Other dependencies are resolved using __meta_design__ accumulated from all parent packages. You can use this to inject anything you need during the run configuration creation.

Here is an example of submitting an injected variable to a ray cluster as a job:
```python


@dataclass
class RayJobSubmitter:
  _a_run_ray_job: Callable[..., Awaitable[None]]
  job_kwargs: dict
  runtime_env: dict
  preparation: Callable[[], Awaitable[None]]
  override_design_path: ModuleVarPath = field(default=None)
  additional_entrypoint_args: List[str] = field(default_factory=list)
  #here you can set --xyz=123 to override values

  async def submit(self, tgt):
    await self.preparation()
    entrypoint = f"python -m pinjected run {tgt}"
    if self.override_design_path:
      entrypoint += f" --overrides={self.override_design_path.path}"
    if self.additional_entrypoint_args:
      entrypoint += " " + " ".join(self.additional_entrypoint_args)
    await self._a_run_ray_job(
      entrypoint=entrypoint,
      runtime_env=self.runtime_env,
      **self.job_kwargs
    )


@injected
def add_submit_job_to_ray(
        interpreter_path,
        default_working_dir,
        default_design_paths: List[str],
        __resolver__: AsyncResolver,
        /,
        tgt: ModuleVarSpec,
) -> List[IdeaRunConfiguration]:
    """
    We need to be able to do the following:
    :param interpreter_path:
    :param default_working_dir:
    :param default_design_paths:
    :param ray_runtime_env:
    :param ray_client:
    :param tgt:
    :return:
    """
    # Example command:
    # python  -m pinjected run sge_seg.a_cmd_run_ray_job
    # --ray_client={ray_cluster_manager.gpuaas_ray_cluster_manager.gpuaas_job_port_forward}
    # --ray-job-entrypoint="echo hello"
    # --ray-job-kwargs=""
    # --ray-job-runtime-env=""
    try:
        submitter:RayJobSubmitter = __resolver__.to_blocking()['ray_job_submitter_path']
        # here we use dynamic resolution, since some scripts don't have ray_job_submitter_path in __meta_design__
    except Exception as e:
        logger.warning(f"Failed to resolve ray_job_submitter_path: {e}")
        raise e
        return []

    """
    options to pass secret variables:
    1. set it here as a --ray-job-kwargs
    2. use env var
    3. upload ~/.pinjected.py <- most flexible, but need a source .pinject.py file  
    
    """
    tgt_script_path = ModuleVarPath(tgt.var_path).module_file_path

    conf = IdeaRunConfiguration(
        name=f"submit_ray({tgt.var_path.split('.')[-1]})",
        script_path=str(pinjected.__file__).replace("__init__.py", "__main__.py"),
        interpreter_path=interpreter_path,
        arguments=[
            "run",
            "ray_cluster_manager.intellij_ray_job_submission.a_cmd_run_ray_job",
            f"{default_design_paths[0]}",
            f"--meta-context-path={tgt_script_path}",
            f"--ray-job-submitter={{{submitter}}}",
            f"--ray-job-tgt={tgt.var_path}",

        ],
        working_dir=default_working_dir.value_or("."),
    )

    return [conf]


```


# Appendix
## Why not Pinject?

Although pinject is a good library for dependency injection, the style it provides for specifying dependency binding was
tiring to write.

```python
# Original pinject:
import pinject
from dataclasses import dataclass
@dataclass
class SomeClass(object):
    foo:str
    bar:str

class MyBindingSpec(pinject.BindingSpec):
    def configure(self, bind):
        bind('foo', to_instance='a-foo') #side-effect here
        bind('bar', to_instance='a-foo')
class MyBindingSpec2(pinject.BindingSpec):
    def configure(self, bind):
        bind('foo', to_instance='b-foo')


obj_graph = pinject.new_object_graph(binding_specs=[MyBindingSpec()])
some_class = obj_graph.provide(SomeClass)
print
some_class.foo
'a-foo'
```
## Pinjected version
```python
from pinjected import Design, instances, providers
from dataclasses import dataclass
@dataclass
class SomeClass(object):
    foo:str
    bar:str

d:Design = instances() # empty immutable bindings called Design
d1:Design = instances( # new Design
    foo="a-foo",
    bar="a-bar"
)
d2:Design = d1 + instances( # creates new Design on top of d1 keeping all other bindings except overriden foo
    foo="b-foo" #override foo of d1
)
a = d1.to_graph()[SomeClass]
assert(a.foo == "a-foo")
b = d2.to_graph()[SomeClass]
assert(b.foo == "b-foo")

```
This library makes pinject's binding more portable and easy to extend.

# Update Logs
- 0.2.115: Updated documentation structures.
- 0.2.40: Added support for overriding default design with 'with' statement:
```python

run_train: Injected = train()

with providers(
        val_loader=one_sample_val_loader,
        train_loader=one_sample_train_loader,
        training_loop_tasks=Injected.list()
):
    test_training: Injected = training_test() # here, test_training will use the overridden providers! 
    with instances(
        batch_size=1:
    ):
        do_anything:Injected = task_with_batch_size_1() # you can even nest the 'with' statement!

```

