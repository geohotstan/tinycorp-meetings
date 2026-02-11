# consensus-talk Meeting

### Audio

https://consensus-hongkong.coindesk.com/agenda/event/-open-source-ai-in-your-pocket-a-case-study-77

### Transcript
##### **Qazalin** [00:00:14]

All right, so I understand that this is more of a crypto audience.
I'm sure many of you have heard of Nvidia. It's the largest company in the world: $4 trillion of market cap.
By comparison, Nvidia is worth double all of crypto combined.

So what do they do exactly?
Well, they make these AI chips that run everything from robotics models to large language models, agents, and they sell them for a lot of money.
It's an honest business: they sell them for more than they cost to make.

And the customers are finding it useful and valuable.
Many are using it: Tesla, Google, Amazon, everyone big and small are using Nvidia to train their models.

So you might be thinking that it's actually a very good chip.
Well, this is a comparison chart between Nvidia and their closest competitor for the chips that they make.
You don't need to worry about the actual metrics. Just know that higher is better.

So Nvidia is the most valuable company in the world, right? So they must be the better one.
Who here thinks Nvidia is the gray one or the blue one?
Gray one? It's actually the other one. Let's call the other one gray.

Who's the red team? Who's the red company?
Is it like a secret government operation? Maybe it's privately held.
No, it's called AMD. It's pretty small by comparison.

This is the chart of the market cap of Nvidia and AMD. This is when ChatGPT launched.
Something is going on here: people actually use these AI chips.

There are people talking about how AMD is not competitive. Their experience is suboptimal.
People can't use the chips out of the box.

Let's go back to this chart and stay here for a bit and label this for you.
This is Nvidia versus AMD hardware comparison.
AMD is the red team, Nvidia is the green team. 

The three metrics are the three foundational metrics we care about when we are trying to talk about hardware the run AI models. The first one is compute. This is basically how much work your agents can do at the same time. 

So the higher it is, the more work your agents can do, or the more work the robots can do.

Higher compute is better. AMD is clearly winning here.

The second one is memory capacity. We care about this a lot because we want our models to be big.
LLM stands for large language model. These foundation models are incredibly big, and they're supposed to hold the entire Internet.
Again, AMD is much better than Nvidia at this. They have many tricks, like chiplets that they use.
They have so many different capabilities, and Nvidia is really just not competitive in that regard.

The third one is memory bandwidth. This is how fast your model runs (tokens per second).
It's similar to Internet bandwidth: the higher it is, the faster your connection, the faster your tokens per second are.
So we really care about this.

From this chart, the red team is clearly winning at hardware.
So why isn't AMD the most valuable company in the world?

Nvidia is a software company. And we're here to talk about the software.
This is often overlooked, but there's actually so much that goes into making AI runnable as products.
The process of going from AI research to actually making a product goes through many, many layers.

So on the top, you might see these logos, and you might be very familiar with them.
There's OpenAI. There's DeepSeek. These are the foundation models that we interact with every day.

But then below that, we have the developer tooling.
And then after that, we have all the runtime stuff.
And finally, we go to the actual hardware.

You see that every single one of these is a green box.
Everything below the application layer becomes vendor-specific.

The moment a company like OpenAI starts to invest money into products, they're going to start democratizing an AI model.
They start to put all their engineering effort on a single platform.
And they become completely locked into that platform in the end.

So we end up in this situation where once you use Nvidia, it becomes very hard to switch.
Sadly, Red Team is doing something very similar.

Now if Nvidia had something like CUDA Graphs, well, it's not going to work. AMD has hipGraph.
Nvidia had NCCL. AMD has RCCL.

So they're basically copying Nvidia.
And this means that if a company wants to switch to AMD, now they have to rewrite their entire stack.
This is going to take many engineering hours, many hours of work, and it's just not viable for many of these people.

Okay. So we're here to talk about an alternative.

##### **Geohot** [00:06:55]

Hi, everyone. All right.

Look, Nvidia actually is the most valuable company in the world. Over $4 trillion.
I think people don't really think about this enough.

So what do you do if you're a competitor?
You skate where the puck has been, right? It's a literal clone.
AMD is like, "Oh, we're just going to clone every single piece of Nvidia."
And this actually kind of works. This gets them some market share, but that's not what I'm here to do.

I look around at the world today, and I see all of this value, right?
But is this value real? Is any of this value real, or is it all just because of moats?
How do you completely destroy all the moats in AI?

And our slogan is to commoditize the petaflop.
So the petaflop is the foundational unit of AI compute. And we want to turn the petaflop into a commodity.

So this is TinyGrad. TinyGrad replaces all of that vendor software with 20,000 lines of code.
And this isn't some, like, hypothetical abstraction. I'm not trying to shill you on anything.
It's free MIT software. But we've replaced the entire vendor stack with 20,000 lines of code.
And then in order to add a new vendor, you have to write about 300 lines of code.

We support Nvidia, AMD, Apple, Qualcomm.
People have ports for Rockchip. People have ports for Tenstorrent.

So the idea is that the FLOP should be a commodity in the same way electricity is a commodity.
And when you look at the difference in these stacks, when you look at how much less code you actually need,
and how much of this code does not have to be vendor-specific, but is chosen to be vendor-specific to justify
Nvidia's $4 trillion valuation, yeah.

So... it's on GitHub. It's free.

And, you know, I think about what I want to do with my life.
And, you know, some people want to, like, make a lot of money. And I'm like, what am I going to do with a lot of money?
What am I going to do? Like, buy, like, jets and bottles at the club or whatever? You know, it's kind of boring.

But, like, imagine you could destroy $3 trillion, right? Like, think about that.
What actually happens if the petaflop becomes commoditized?

Something doesn't make any sense here.
AMD has more FLOPs per dollar than Nvidia. Yet one company's market cap is that and one company's market cap is that.

Part of this might be because the markets are incredibly short-sighted.
And people are like, "But Nvidia is making so much revenue right now."
And, well, you know, you can believe that, right? You could also see what the...

I don't know if you guys are familiar with how Nvidia's circular dealing works.
Like, if anyone out there wants to start a company, I'll start a company, too.
We'll both raise $10 million. We'll pass the money back and forth. Repeatedly.
We'll both have a billion dollars in revenue. We'll raise on our revenue, right? Like, it's a good idea, right?

So, yeah. Why can nobody use the other AI chips? It's because Nvidia has software.
Nvidia tries to lock you into this software.

If TinyGrad actually succeeds at replacing all of this vendor software with something generic,
you know, what happens to the vendor lock-in? This has happened before.
This is what Linux was. This is what LLVM was.
And, you know, my hope is to build the next one of those things.

So, yeah. I don't know what else I'm going to talk about for three minutes and 40 seconds.
It's more like having a computer here. So I could actually, like, demo some TinyGrad for you guys.
But, yeah, no.

I mean, like, my dream is not even just Nvidia versus AMD, but it's...
Yeah. I'm not going to talk about that.

I'm going to talk about the fact that 20 identical-looking Chinese companies all compete to all tape out identical accelerators.
You know how cheap it is to get CNC work done in Shenzhen? Imagine that was true.

So you can think about the AI stack in terms of five tiers, right?
Like at the top, you have things like Cursor and Windsurf. These things are totally worthless. Everybody knows that now.
Look at the billions that were paid for Cursor and Windsurf to just watch Claude Code come out
and completely blow their moat away.

And the moat's not even in Claude Code. It's in OpenCode. I can use OpenCode in Kimi.

So it's even unclear that these Tier 4 companies, like OpenAI and Anthropic, are going to be where the value is.
Then you get down to the Tier 3 companies, the NVIDIAs and the AMDs.

So Tier 5 is commoditized. It's beyond commoditized. Nobody cares about Cursor anymore.
Tier 4 is becoming commoditized.
The Chinese are really trying to commoditize their competition.
You have Kimi, you have DeepSeek, you have Qwen. You have...

And then you have the Tier 3s, which aren't commoditized yet, which is where we're working.
Then you have the Tier 2s, like TSMC. How do we commoditize that?
Then you have the Tier 1s, like electricity. I mean, that's already a commodity.

So how do we commoditize the entire AI stack?
And to get rid of all the premium, you're paying a premium for green FLOPs every time you run a model.
And you're like, "Oh, I don't buy any NVIDIA. This doesn't apply to me."
Yeah, but do you use tokens? Do you use ChatGPT? Look at how overvalued it is. It's not worth it.

And NVIDIA's margins are also insane.
The H100 had a 91% margin. The B200, they backed off a little.
They backed off a little. The B200 has like an 80% margin. Just 80%, guys.

But, yeah, so... does anyone know what any of this code is?
Who's heard of any of the things on the board, right? But they use all of them.

Like, cuDNN is your GEMMs and your comms.
CUTLASS is now replacing that with a new thing. You can use cuTILE, the latest thing in Python.

NCCL is the NVIDIA collective communications library.
RCCL is the ROCm collective communications library, right?

cuSPARSE. rocSPARSE, right?
HIP... this doesn't work. Right? This is not where things are going to go.
Things are definitely going to go to something that looks like this.

And then... how can we move down that value chain as much as possible, commoditize every single piece of AI?
Because the best thing that you can possibly hope for...
This is true for crypto mining, too.

The best thing that you can possibly hope for for the future is that it's linear.
Right? Big billionaires are going to own tons of intelligence. Everybody already knows this.
The question is, is that scaling function...
It's definitely not going to be sublinear. You're not going to have any advantage having $1,000 versus their billion.
But it might be something that's going to be a little bit more complex.
But it's going to be linear. And that's the best we can hope for.
Where you get a perfectly linear amount of the intelligence.

And commoditizing the petaflop is one step towards making that happen.
And then commoditize the chip production, commoditize the electricity, commoditize everything if you want to live in a good future.

All right. That's our talk.
