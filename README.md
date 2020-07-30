# Strong Graphs
A graph generator for strongly connected directed graphs with controllable features.

Generate the following 💪 graphs with this command
``` #python 
python3 generate.py 20
```
[logo]: docs/20-complete.png "Logo Title Text 2"
![alt text][logo]

### Complexity
The intended complexity of the generator is O(n + m). Currently I have O(n log n + m) I believe, with the log n coming from having to order the nodes by distance in order to add negative arc weights in a control way.