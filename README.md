# CVMAlgorithm

To build the animation run
`manim -p -ql cvm.py CVM`

it will leave a .mp3 file in
`media/videos/cvm/720p30/CMV.mp3`

The CVM algorithm (named after the authors - read it [here](https://arxiv.org/pdf/2301.10191)) is about estimating the number of distinct elements in a stream when memory is a constraint. Normally, if a set has `n` unique elements you need to store at least `n` elements (all of them). In this case we can store `m` elements, where `m` << `n`.
 
The algorithm pseudocode is under 10 lines long:
- start with `p` = 1
- for each element `a` in the stream: add `a` to the memory set `X` with probability `p` (if not already present)
- each time the memory set is full: remove some elements with fixed probability 1/2 and update `p` by halving it (p /= 2)
- when the end of the stream is reached: output `|X| / p`, i.e. the cardinality of the memory set over the sampling probability `p`

Why is that? The first question was: "how come `|X| / p` estimates the number of unique elements?". Well, it wasn't immediately clear to me but I figured out the core intuition is this: if I tell you I am picking one flower for every four I see, and I currently have 5 flowers in my hands, how many flowers do you think I saw in total? About 20, right? More generally, if I have `K` (5) elements and I picked them all with probability `p` (1/4) , then we can say I have gone through roughly `K / p` (5/(1/4) = 20) elements in total!

Once I saw this and other elements, I wanted to animate it - that's when I thought about manim. The other feature that makes this algorithm visually appealing is that all the probabilities are powers of 1/2, so we can think about them in terms of Bernoulli trials (read, coin tosses).

In this simulation the memory has size 5, the stream has 50 elements in total and 26 unique elements by design (the letters of the alphabet). The algorithm estimates 24 unique elements using 1/10th of the memory - we could also say using 5 fingers and a coin! Not bad, uh?

At this point other questions you might have are: 
- why clearing the memory with fixed probability 1/2? 
- why halving the probability in each round? 
See if you can get an idea from the animation…! 

