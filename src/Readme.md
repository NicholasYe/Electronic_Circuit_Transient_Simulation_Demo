
**This is the instruction of how to convert an electrical circuit into a connection dictionary.**

## Node Diagram Definition

We use the definition of components between nodes to describe the connection method of the circuit. For each diagram, it is necessary to define the number of nodes in the circuit, and we do not need to specify which node is connected to the ground but we require it to be specified in the later simulation.

First, assume that we have a circuit that have four nodes, then we can construct an empty diagram like this:

```
    |  U1  |  U2  |  U3  |  U4  |
----|------|------|------|------|
 U1 |  --  |  --  |  --  |  --  |
----|------|------|------|------|
 U2 |  --  |  --  |  --  |  --  |
----|------|------|------|------|
 U3 |  --  |  --  |  --  |  --  |
----|------|------|------|------|
 U4 |  --  |  --  |  --  |  --  |
```

This diagram contains no electrical components yet, but it is easy for us to find out how every electrical component is connected to the nodes after we fill in as well as how these node is connected to each other.

## Element definition

Before we start to fill in the component into the diagram, it is necessary to specify the direction of each component and some special characteristic of some components.

### The ground

We automatically define the last node of the node diagram as the ground. In the four nodes example, it is the U4 node.

You can not specify the ground in the program but if you want to change the ground location, you can simply change the connection diagram.

### DC Source

From Norton's theorem, it is obvious that every DC voltage source with a resistor in series can be replaced by a DC current source with a resistor in parallel. 

Assuming a voltage source is connected with node u1 and u2, and we specify u1 node is the positive side of the source while u2 is the negative side of the source, then we can write the component in the connection diagram like this:

```
    |  U1  |   U2   |
----|------| ------ |
 U1 |  --  | ["V1"] |
----|------| ------ |
 U2 |  --  |   --   | 
```

Nevertheless, if a voltage source is connected with node u1 and u2, but we specify u2 node is the positive side of the source while u1 is the negative side of the source, then we can write the component in the connection diagram like this:

```
    |   U1   |  U2  |
----| ------ |------|
 U1 |   --   |  --  |
----| ------ |------|
 U2 | ["V1"] |  --  |
```

Another character we need to notice is the current of the source, in both situation, we all assume that the current of the source is floating from the high voltage to lower voltage, which means in the first example, the current of the source is flowing from u1 to u2, and in the second example, the current of the source is flowing from u2 to u1.

### Resistor

Resistor is a component that do not have any constraint such as voltage and current, so we can write the resistor in the connection diagram like this:

```
    |  U1  |   U2   |
----|------| ------ |
 U1 |  --  | ["R1"] |
----|------| ------ |
 U2 |  --  |   --   | 
```

Also, the current passing through the resistor component is from U1 to U2.

### Capacitor

Capacitor is a component that do not have any constraint such as voltage and current, so we can write the capacitor in the connection diagram like this:

```
    |  U1  |   U2   |
----|------| ------ |
 U1 |  --  | ["C1"] |
----|------| ------ |
 U2 |  --  |   --   | 
```

Also, the current passing through the capacitor component is from U1 to U2.

### Inductor

Same as the capacitor, inductor is a component that do not have any constraint such as voltage and current, so we can write the inductor in the connection diagram like this:

```
    |  U1  |   U2   |
----|------| ------ |
 U1 |  --  | ["L1"] |
----|------| ------ |
 U2 |  --  |   --   | 
```

Also, the current passing through the inductor component is from U1 to U2.

### Switch

Diode is a different component from above since it can be controlled by human, but do not have any constraint, so we can write the switch in the connection diagram like this:

```
    |  U1  |   U2   |
----|------| ------ |
 U1 |  --  | ["S1"] |
----|------| ------ |
 U2 |  --  |   --   | 
```

Same as above, the current of switch is from u1 to u2.

### Diode

Diode is a special kind of switch since it only allows current to flow in one direction, so we need to specify the direction of the current flow. 

If we assume that current is only allowed to flow from u2 to u1, then we can write the diode in the connection diagram like this:

```
    |  U1  |   U2   |
----|------| ------ |
 U1 |  --  | ["D1"] |
----|------| ------ |
 U2 |  --  |   --   | 
```

In other words, if we have a diode that allows the current to flow from u1 to u2, then we can write the diode in the connection diagram like this:

```
    |   U1   |  U2  |
----| ------ |------|
 U1 |   --   |  --  |
----| ------ |------|
 U2 | ["D1"] |  --  | 
```

Same as above, the current of diode is from u1 to u2 in first example while the second example is opposite.

## Connection Diagram

After we have defined the direction and constraint of each component, we can start to fill in the component into the diagram.

### Buck Circuit

![](image/Buck_Circuit.png)

- This is how the matrix is constructed:

```
    |    U1   |   U2   |   U3   |     U4      |
----|---------|--------|--------|-------------|
 U1 |    0    | ["S1"] |   0    | ["V1"]      |
----|---------|--------|--------|-------------|
 U2 |    0    |    0   | ["L1"] | ["D1"]      |
----|---------|--------|--------|-------------|
 U3 |    0    |    0   |   0    | ["C1","R1"] |
----|---------|--------|--------|-------------|
 U4 |    0    |    0   |   0    |     0       |
```

### Boost Circuit

![](image/Boost_Circuit.png)

- This is how the matrix is constructed:

```
    |  U1  |   U2   |  U3  |     U4      |
----|------|--------|------|-------------|
 U1 |  0   | ["L1"] |  0   | ["V1"]      |
----|------|--------|------|-------------|
 U2 |  0   |    0   |  0   | ["S1"]      |
----|------|--------|------|-------------|
 U3 |  0   | ["D1"] |  0   | ["C1","R1"] |
----|------|--------|------|-------------|
 U4 |  0   |    0   |  0   |     0       |
```

## Philosophy of Connection Matrix

The philosophy of building up this matrix is that the no matter in what situation, the current flows from higher voltage places to lower voltage places. 
