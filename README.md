# Strong Graphs
A graph generator for strongly connected directed graphs with controllable features.

[logo]: docs/fast.gif "Complete Graph Generation"
![alt text][logo]

[logo]: docs/strong.gif "Complete Graph Generation"
![alt text][logo]

Generate the following 💪 graphs with this command
``` #python 
python3 generate.py 20
```

[logo]: docs/20-complete.png "Example Graph"
![alt text][logo]

### Complexity
The intended complexity of the generator is O(n + m). Currently I have O(n log n + m) I believe, with the log n coming from having to order the nodes by distance in order to add negative arc weights in a control way.