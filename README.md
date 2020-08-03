# Strong Graphs
A graph generator for strongly connected directed graphs with controllable features.

* Example 1. Complete graph with 50% negative arcs

[logo1]: docs/fast.gif "Complete Graph Generation"
![alt text][logo1]

* Example 2. As many negative arcs as possible

[logo2]: docs/strong.gif "Complete Graph Generation"
![alt text][logo2]

Generate the following 💪 graphs with this command
``` #python 
python3 generate.py 20
```

[logo3]: docs/20-complete.png "Example Graph"
![alt text][logo3]

### Complexity
The intended complexity of the generator is O(n + m). Currently I have O(n log n + m) I believe, with the log n coming from having to order the nodes by distance in order to add negative arc weights in a control way.