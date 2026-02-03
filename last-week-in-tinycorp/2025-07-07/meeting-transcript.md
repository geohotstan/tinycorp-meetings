# 2025-07-07 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company updates
- can tinygrad win?
- app ollama
- mlperf LLaMA 405b
- viz tool
- drivers
- cloud
- onnx
- symbolic stuff (div 0 view)
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=DSWQCT9mypQ)

### Highlights

- **[Company Updates](#geohot-000007)**: TinyBox screens are in stock, with only one TinyBox Red unit remaining. New AMD machines, for which a tracking number was received, have been delivered.

- **[Can tinygrad win?](#geohot-000158)**: Geohot critiques the MLIR philosophy of building a framework with many specialized parts, comparing it to Waymo's approach. He argues tinygrad's path to victory is by embracing the "bitter lesson"—leveraging large-scale search and optimization to be consistently faster across diverse models and hardware.

- **[Ollama App](#geohot-002634)**: Geohot is finalizing a simple, 150-line, pure tinygrad Ollama app to give users an immediate, useful tool post-installation. He notes the models can lose coherence, but the simplicity of tinygrad's implementation makes it easier to debug and improve.

- **[Core Refactor](#geohot-003110)**: Geohot plans to refactor the optimization process, starting by fixing the issue of calling `simplify` at every step. This change will enable `opt-ops` to be applied in parallel and to target specific parts of the graph (like a reduce op) rather than only the sink.

- **[MLPerf LLaMA 405B](#chenyu-003514)**: Chenyu is working on the dataset preparation for the LLaMA 405B benchmark. He is trying to replicate the complex data packing methods, potentially using NVIDIA's Nemo as a reference, as this was a missing detail in Google's withdrawn submission.

- **[Viz Tool](#qazalin-003954)**: Qazalin demonstrated updates to the tiny-device viz tool, which now includes a Python timeline. Future plans include detailed buffer tracking to differentiate memory usage (e.g., model weights vs. activations). Geohot suggested also visualizing the individual rewrite steps within the `get_program` timeline.

- **[Drivers](#nimlgen-004814)**: The custom NVPCI driver with huge pages now shows performance that is competitive with, and often better than, the official NVIDIA driver on single-device tests. The team plans to conduct more stability testing, merge it into CI, and add support for the 5090.

- **[Cloud File System](#geohot-005518)**: Progress continues on the distributed file system, with a version expected to be deployed this week. A key goal is to integrate the local download cache, ensuring all file access (from URL or hash) uses the same unified, hash-based backing store.

- **[Symbolic Engine](#sieds_lykles-010311)**: A bug in symbolic simplification has been fixed and the PR is ready to be merged again. A new fuzzer is uncovering edge cases, particularly around integer overflow in symbolic comparisons. The consensus is to treat overflow as an implementation detail and keep the high-level symbolic rules abstract.

- **[Bounties](#chenyu-011123)**: Flata has completed the retinanet rewrite bounty and is now debugging its performance. Geohot clarified the `setitem` bounty, explaining the goal is to generate a single kernel with multiple individual store operations, not a loop.

### Transcript

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=7)]
TinyBox screens are pretty much in stock. We got another order, we sold one more TinyBox. Red, so there's actually one TinyBox Red left. TinyBox screens are flowing now, I think I'll send out a marketing email this week. Also AMD supposedly sent us a FedEx tracking number, but last time I checked it, it didn't work. Let me try it again. Oh, that's full of machines. Wait, what? I have a lot of questions about this. We got something else about the contract too, I have a lot of questions about it, but we'll see. We have a FedEx tracking number. It doesn't even look like, oh, wait, what? Delivered. Oh, we got blocks. No, no, this is something else. Who can use the Internet, so hard to use. You're in the tracking number? No, the tracking number can't be found right now, so I don't know about that. No box. Okay. Okay, great.

##### **Chenyu** [[00:01:55](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=115)]
Everyone want to discuss your blog post?

##### **Geohot** [[00:01:58](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=118)]
Yeah, I mean, I think the main thing really to discuss is to realize that MLIR is just the way my approach to neural networks. It's the same thing, right? It's this idea that you're going to be able to build a framework that's flexible enough to capture everything. And then you'll just have the framework and you'll have different people work on each part of the framework, and the different people, some people work on convs, some people work on speed limit signs. And then it'll all come together and create a great system that's going to outperform everything. And I just don't think this is true. I think it's the exact same thinking that leads to Waymo. MLIR has a conv 3D guy whose job it is to do conv 3Ds. Oh, and even worse, he's doing conv 3Ds and you and data on AMD. Like, this just isn't going to work. I mean, I guess imagine how people would just winograd.

##### **Chenyu** [[00:03:14](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=194)]
I mean, Winograd only works because someone looked into conv. Like, I'm always, Winograd really only works for small convs.

##### **Geohot** [[00:03:27](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=207)]
Winograd's a little bit different from what I'm talking about, right? Winograd actually changes the compute itself.

##### **Chenyu** [[00:03:35](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=215)]
Yeah, that's what I mean.

##### **Geohot** [[00:03:38](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=218)]
Well, yeah, but I mean, we're always going to be able to express things like Winograd at a higher level. I'm talking about when you have the compute that's fixed, you need to determine how to properly schedule that compute. You know the graph, and you're asking the question, how do I best schedule this graph across this hardware, across these 20 GPUs?

Yeah, so I think the bitter lesson has to win here.

##### **Chenyu** [[00:04:11](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=251)]
There's no more elaborate model for low sentence.

##### **Geohot** [[00:04:17](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=257)]
Well, there's no way that as these systems continue to grow and get more complex, there's going to be more and more compute put into it. So you're just going to be able to do a lot of tuning basically. If you're about to run a huge training run, the only thing you care about is the overall cost of the run. So you want something that continues to scale with more input compute. You want something that continues to get faster. You're like, okay, well, I'm about to do a huge search to figure out how to make this thing as fast as possible.

##### **Chenyu** [[00:04:51](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=291)]
Yeah, but what's happening to LLM is there's literally just three components to LLM training and they just make it repeated multiple times.

##### **Geohot** [[00:05:02](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=302)]
Yeah, like so yours.

##### **Chenyu** [[00:05:05](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=305)]
So, I guess what you're saying is true is in the world has a huge diversity, like huge diverse models that it's impossible to hand tune each of them. Like how can we ever?

##### **Geohot** [[00:05:19](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=319)]
I mean, if it's true that the world is just literally only LLM, then this probably doesn't make much sense. But I mean, the world just, like even today we're already seeing what the success of the transformer architecture is. It's diffusion. Like there's going to be aspects of the transformer that continue over, but like Comma has moved away from all our video gen models are diffusion. They're not transformers. And I don't think that this really stops. I don't think that there's going to be a massive collapse into a single model type.

##### **Chenyu** [[00:06:05](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=365)]
Yeah, but let's say maybe it's not one, but let's say 10. I don't even think it's going to be 10.

##### **Geohot** [[00:06:18](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=378)]
I think that the reason you're getting this, the reason right now you're seeing so much stuff be shoehorned into a transformer even when maybe it shouldn't is because the minute you step away from the beaten path of transformers, everything becomes a lot harder to run. If you think about the engineering years that have gone into optimizing transformers, the minute you step away from that, you no longer have that. So even if your new architecture is better, it's not optimized.

##### **Chenyu** [[00:06:50](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=410)]
Yeah, but this is just, I mean, then will there be your time for it's too late. I say if you want to start a brand new operating system, because of the new design and new learning and you find all the problems in Linux. And Linux has grown like this super big in transfer light on and complexity. Well, so that also fits in that. Now how does this new operating system with the new best principle going to win?

##### **Geohot** [[00:07:22](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=442)]
Yeah, I mean, I think that Linux is, if I came up with a new operating system, how do you compare and contrast that to Linux? How do I make an argument that my operating system is better?

##### **Chenyu** [[00:07:37](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=457)]
You can pick certain hardware and certain workloads and say your operating systems perform these workloads better on these hardware. How we are doing now for tinygrad compared to other stuff, right?

##### **Geohot** [[00:07:49](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=469)]
Well, no, but it's different, right? Like most of the reason that somebody chooses an operating system does not come down to the performance of the operating system. Also, I think people choose an operating system a lot more for reasons like app interoperability, for example.

##### **Chenyu** [[00:08:11](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=491)]
Okay, then why is that not the case for deep learning compilers?

##### **Geohot** [[00:08:16](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=496)]
Because the apps are so simple. There is nothing in deep learning that today you can't re-specify in a day. There's no model that's more complicated than what you could write in a day in tinygrad. And fully specified model exactly. Whereas if you ask me to write Chrome, that's hopeless. Okay, so because the app is very simple. I think so, yeah.

##### **Chenyu** [[00:08:50](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=530)]
So which pretty much translates to switching costs is fairly low.

##### **Geohot** [[00:08:55](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=535)]
Exactly. Yeah. I think the switching cost from framework to framework is low. Well, there's also like, that's true. Like the switching cost is low. Yeah. Well, I mean, neural network framework includes a lot of different things. And I think in the future, we'll have better words to talk about all of these, but like switching from, if I have something that's running in ONNX, I'll switch in a minute. The cost of switching from ONNX runtime to something else. Now, if I have a huge codebase and ecosystem in torch, yeah, okay, that's a bit harder to switch. But again, okay, that's why just be a backend to torch.

In the same way that both BSD and Linux can run C code or can run Python. Like if I have a Python library, I can run it probably just as easily on Linux and BSD. Okay. Yeah, I think there's some.

Like I'm not saying that we're going to succeed at this goal. But I believe that if we do succeed at this goal that there isn't anything else. I believe that if we can consistently run things faster across a huge set of architectures and a huge set of different models, I think we have to win and make the switching cost low. But I actually think we're good enough on that front. I think today if tinygrad were 30% faster, a lot of people would be switching.

##### **Chenyu** [[00:10:43](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=643)]
Yeah, the problem is, does it look like a uniformly 30% faster or for some things it's faster or some things slower? Because many stuff in tinygrad is pretty slow.

##### **Geohot** [[00:10:54](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=654)]
Well, so let's compare that to self driving cars. My theory is that it's mixed at the beginning. And then the end to end approach just starts to pull away. So at the beginning you'll find right now there's some things that are faster in tinygrad and some things that are faster in torch. Most things are faster in torch, like our GEMMs are just bad.

##### **Chenyu** [[00:11:24](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=684)]
There are a lot of stuff that we just in principle don't support. Like what has a for loop, conditions, and some fancy CPU stuff.

##### **Geohot** [[00:11:38](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=698)]
Yeah, I'm not sure this is a problem. You can always just keep that in whatever other framework you want. That stuff's usually not, like I don't know any neural networks that have that stuff deeply embedded in it.

##### **SPEAKER_09** [[00:11:52](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=712)]
Okay, I don't know either.

##### **Chenyu** [[00:11:54](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=714)]
For loop. Yeah, I mean we can. That's the thing I could think kind of is part of this right because we are. So this is definitely a limit. Say for example, we probably don't support user, insert arbitrary code into as a or something like that.

##### **Geohot** [[00:12:13](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=733)]
Yeah, I don't think we should support stuff like that. I think there might be a way to encapsulate user code in such a way that's pretty isolated from the rest of the graph. But of course that's not going to be fast. But I really don't think this is much in terms of for loops and conditionals and we should support for loops. We should support things like RNNs. That's just range of the overworld. When it comes to if statements, well, why do you need an if statement and not a where?

##### **Chenyu** [[00:12:45](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=765)]
It's weird to compute both.

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=768)]
That's implementation. It doesn't matter. Oh, right.

##### **Chenyu** [[00:12:55](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=775)]
That's the reason why np's np's.

##### **Geohot** [[00:13:00](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=780)]
What you're saying is you won't be able to search correctly for the branches of the where. But no, my point is, I mean, you say that this is a feature we don't support much. Well, you say it's a feature we don't support in where, like there are some conditionals you actually can't express as a where. And those conditionals we don't support.

##### **Chenyu** [[00:13:22](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=802)]
But it's a part of the dependent. We can't support it. It's just not jittable. What do you mean by data dependent? Like where is data dependent? No, no, depends on say like nonzero or something that requires you to evaluate part of the stuff for your second part. Because it's a shape related stuff.

##### **Geohot** [[00:13:47](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=827)]
Oh, I mean dynamic shape. Sure. Yeah, we don't support dynamic shapes. Yeah, everyone should move away from dynamic shapes.

##### **SPEAKER_09** [[00:13:58](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=838)]
Yeah, but true.

##### **Geohot** [[00:14:03](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=843)]
That is one clear example of something we will never support. Yeah. There's a few fast top K that need data dependent branching. Yeah, I think that. But there's definitely ways to write top K that don't need data dependent branching. Data dependent branching is a really bad idea. Data dependent branching is a branch mispredict and a pipeline stall. That's the stuff that makes code unpredictable. So no, I don't know. I'll bet there's no major neural network that has any data dependent branching stuff.

##### **Chenyu** [[00:14:46](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=886)]
Yeah, it's okay. So we want this target neural network to be simple enough, but not too simple. But we have a chance.

##### **Geohot** [[00:14:56](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=896)]
Well, we want it to be expressible. Like, yeah, in this language. Sure, you're right. If the world of neural networks becomes too simple or too complex, we lose in both cases. If it becomes too simple that it's just literally, well, I want to just use the transformer, I want to just use this one trick, then yeah, okay, there's no winning there. That just will be super optimized by things that can explicitly code for it. And then if it's too complex, it just starts to look like code again. And then actually probably like an LLVM MLIR style approach wins.

##### **Chenyu** [[00:15:40](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=940)]
And I guess it also depends on how big your user team is, right? Like people in general saying some of their projects depend on MLIR. I'm pretty sure they probably don't need every piece of MLIR, but the fact that they can pick a subset and just work on a subset, maybe works for their approach.

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=958)]
No, but I think that this all just goes away. I actually think that, let's see if we can understand, like my project is based on that ecosystem. The problem with MLIR and things that look like that are, it's really easy to get a foothold, like, oh, I'm going to use this. It's kind of like React, like you just, oh, yeah, of course, we're based on MLIR. But I think that what happens here is all of the code they write just kind of becomes redundant, not redundant, but useless.

Like, what do you think? Well, I mean, it's just why you win. It's just like MLIR might put together a really good guide for how to port to your new accelerator and you just need to support these 162 ops. Okay, yeah, I have a team of people, I can assign them all the ops. It's kind of like the approach that Nvidia and AMD are taking now.

##### **Chenyu** [[00:17:11](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1031)]
I mean, it is another thing for tinygrad. You support 20. Then if you can support 20, why can't you support 200?

##### **Geohot** [[00:17:20](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1040)]
Because our ops, well, I mean, our ops don't really look like their ops, right? Like, conv2d is not an op.

##### **Chenyu** [[00:17:31](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1051)]
Yeah, but how bad can that be?

##### **Geohot** [[00:17:34](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1054)]
Well, the problem is not that just supporting the one op is bad. The problem is not, oh, I'm going to support conv2d. That's not bad. Okay, but what do you type? What about if you're doing weird conv2ds where the batch size is really big, but the channels out is one. Like, is that going to affect?

##### **Chenyu** [[00:17:56](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1076)]
Our tensor.py is only 2000 lines and it has a piece of that, right?

##### **Geohot** [[00:18:03](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1083)]
Well, yeah, no, no, but our tensor.py is not a, our tensor.py, hey, Light really talks about this well. Our tensor.py is not the, our tensor.py is the spec, it's not the schedule.

##### **Chenyu** [[00:18:19](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1099)]
Yeah, but I mean, I don't know, back to a dtype problem. I don't see why you cannot just duplicate and implement everything, your 10 dtypes.

##### **Geohot** [[00:18:33](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1113)]
Well, okay, now you're not implementing 200 anymore, you're implementing 2000.

##### **Chenyu** [[00:18:37](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1117)]
Yeah, but I'm pretty sure I have AI and they can just copy paste everything for me.

##### **Geohot** [[00:18:42](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1122)]
Oh, you're going to, okay, you're going to start vibe coding these things. How are you going to check if they're correct?

##### **Chenyu** [[00:18:48](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1128)]
I just want some test.

##### **Geohot** [[00:18:53](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1133)]
Who's going to maintain these? Oh, it's 2000 now. You have 10 dtypes. I don't know. I feel it's not that difficult.

##### **Chenyu** [[00:19:07](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1147)]
And I mean, if ultimately the end user only requires 20 of those to work, who cares if the other 1980 are bad.

##### **Geohot** [[00:19:20](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1160)]
Yeah, sure, right? And if this turns out to be the world that we live in, if the world that we live in, it turns out that all you need to get to work is basically the 10 things we're going to have to make fast for the AMD contract, then yeah, maybe it doesn't matter. But I don't think this is true. I think that like, okay, so now you have.

##### **Chenyu** [[00:19:42](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1182)]
It's kind of true, right? The fact that torch until today still doesn't have uint16 and uint32.

##### **Geohot** [[00:19:52](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1192)]
I could care, someone knows the type. But no, it's not just about those dtypes, right? It's about.

##### **Geohot** [[00:20:02](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1202)]
So if you're like, okay, fine, I'm just going to implement these 10 things and make these 10 things super fast. And then I'll be able to do something like train 405B. Okay, now you want to do it across 10 GPUs. How do you do that? Do you write a sharded form of the kernel? Do you have a separate library you call out into to do the communication? How do you properly overlap that?

##### **Chenyu** [[00:20:35](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1235)]
Just find your network primitives in NCCL.

##### **Geohot** [[00:20:40](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1240)]
Okay, so you find your network primitives in NCCL. Okay, that's great. So what if, yeah, as long as you're using this exactly the way it's intended.

##### **Chenyu** [[00:20:55](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1255)]
No, so I guess my point is now there's no doubt people discuss about Nvidia's mode to being cool or NCCL or whatever chips they have. I always feel it's a lot more about their users and how they are using neural network or developing neural networks. And I think claiming there's a way to win is to find a way for these users to have incentive to use tinygrad other than..

##### **Geohot** [[00:21:27](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1287)]
I think you just have to make it faster. I think you just have to make their workflows faster. Yeah, but the problem is how much faster? I mean, can you be made much faster? Depends what you're doing. If you're doing batch size one LLMs on a single GPU, now of course not. But if you're doing any sort of training job, oh yeah, tons faster. You don't have a really real example of this.

##### **Chenyu** [[00:22:16](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1336)]
Over a slightly more complicated model, right? So I mean like every big training model that kind of requires multi machine or big clusters, or the simple one.

##### **Geohot** [[00:22:32](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1352)]
But even, I mean, you know, just proof that you can continue to.. I got it. I guess it depends what you're comparing to, right? If you compare, look at how much more efficient DeepSpeed is than the other ones. DeepSpeed made it 5x more efficient. And there's a lot more to go there too. I think there's even another 5x.

Well, I mean, it also comes down to being able to repeatedly.. It's so difficult to debug any of this. So Comma, still training on BF16. And sure, we'd like to train with BF8, but you see what happens every time we try to use smaller dtypes. Well, they don't work and then like why don't they work? Okay, which op is it? Okay, let's go through. Let's stick floats in places. Let's see what fixes it. And then I even think it's worse than that. I think that some of the kernels are just broken or numerically unstable or once you get down to these small dtypes.

##### **Chenyu** [[00:23:41](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1421)]
Yeah, but isn't the problem, isn't this argument for specific dtype working because we kind of use a lot of rewriting rules that assumes everything's just perfect real numbers. Yeah, it's just not true for a lot of smaller dtypes.

##### **Geohot** [[00:24:00](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1440)]
I mean, I think we're going to start to need a different approach to some of this stuff. Well, I think the current way that we're doing rewrite rules may not scale. We need to figure out how to leverage more search and optimization. If this wins, this is how we win. We win by having a space that's way more amenable to large scale computerized search and optimization than the competition.

Great.

##### **Chenyu** [[00:24:51](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1491)]
So now we kind of agree that having a conv3D guy is bad, but maybe you need to have a BFLOAT16 guy.

##### **Geohot** [[00:25:00](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1500)]
I don't think so. Nope. So here, there's a good reply to my mode, mode the type guy. There's a good reply to my tweet right here. I'd say general compilers have a lot of hand coded optimizations. Why assume neural network compilers would behave differently. And this is, it's because of the halting problem. It's because there's no way.. Well, you have a neural network kernel. You can benchmark it and every single time no matter what data you put into it, it's going to run in the same amount of time, whereas no normal program behaves like that.

That's, I agree in theory, but is that really the bottleneck why it thinks so. Yeah, I mean, I think it's impossible to reason about code.

##### **Qazalin** [[00:26:08](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1568)]
Okay.

##### **Geohot** [[00:26:22](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1582)]
There was.. I'm just.. I'm discussion.

##### **Chenyu** [[00:26:29](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1589)]
I'm going to follow items that's more onto other items.

##### **Geohot** [[00:26:34](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1594)]
Yeah, just again, the app, I'll have a thing. Yeah, I want to finish it up. I think it's nice. I mean, it gives people a way to pip install tinygrad and do something right away. Is it imports extra? No, it doesn't. It imports nothing. It's 100% pure tinygrad. It's 150 lines and I was playing with it a lot more last night. It's not good. Like I'm still waiting. I don't know if it's the sampler that's bad, but the models just lose coherence after a bit. Which model are you using? I was trying a bunch of the fine-tuned ones. I was doing role playing stuff. They lose coherence after a bit and they just start repeating over and over again. Like it's things you'd never say to actually be to them. So I don't know if that's Ollama with models or bugs, implementation or sampler. Probably model and healthy. There's like 12B models. They're not.. Oh, it's pretty bad. I don't know.

##### **Chenyu** [[00:27:50](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1670)]
I mean, that's not something we will fix with our Ollama implementation, right? Because it loads of sampler does something agreed.

##### **Geohot** [[00:28:03](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1683)]
But the thing about our Ollama implementation is you have hope of fixing it. I was looking into Ollama, trying to figure out the samplers work and it was just spaghetti.

##### **Chenyu** [[00:28:13](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1693)]
You also want to do how Nemo works.

##### **Geohot** [[00:28:16](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1696)]
Okay, anyway, how Nemo works. Oh, that's probably even bigger spaghetti than Ollama. Like Ollama was like, it's fine, you can read it, but well, that's not Ollama, sorry, it's a lot of C++.

##### **Geohot** [[00:28:28](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1708)]
Okay.

##### **Chenyu** [[00:28:32](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1712)]
I think it was generally the problem for maybe MLIR development, similar in a sense that it probably has like 200 different knobs. And if you are an experienced developer, you can keep those. It's like our flags. We probably have like 50 of those. And if you are experienced, you can have those kind of know. But if you are not, the bigger the flag look like, the harder for you to realize what's being..

##### **Geohot** [[00:29:06](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1746)]
I was asking ChatGPT for sampler parameters. I was copying and pasting them. I couldn't tell which ones are really better. No, yeah, we're not going to fix that. But at least we can write something that's very, very simple and repeatable, which I feel like a lot of these things kind of aren't. I think that a lot of these LLM implementations are just broken. But there's no simple way to benchmark them and see that. Like they're getting like 20 points lower on these things, on these like TruthfulQA than they should. But yeah, I don't know. I think it'll be nice to just have, even if it's just the same, it'll be nice to have python -m tinygrad.app.llm.

##### **Chenyu** [[00:29:49](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1789)]
I think it's also good. If you write a clean and easy to adopt one, I think maybe people would be interested to write other apps in that style.

##### **Geohot** [[00:30:05](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1805)]
The only other app we really think about is an image app and it's got to be so simple. Like if we could do an image app also in 150 lines.

##### **Geohot** [[00:30:18](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1818)]
Okay.

##### **Chenyu** [[00:30:23](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1823)]
You block on any of other reflectors for your thing. Oh wait, we did get boxes.

##### **Geohot** [[00:30:31](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1831)]
Oh, it's delivered. There's just a typo on the tracking number. Awesome. Okay. New box.

##### **Chenyu** [[00:30:44](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1844)]
Great. Any other.. Are you blocked on any other reflectors for your thing?

##### **Geohot** [[00:30:54](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1854)]
Not really. They're just.. What? I'm not sure. Oh nice.

##### **Chenyu** [[00:31:00](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1860)]
You mean for the app or for just injector or the core. Refactor many things we want to refactor.

##### **Geohot** [[00:31:10](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1870)]
Yeah. No, I'm not really blocked on anything. I'm just trying to figure out the right order to go about it still. Okay. I think the first thing is just to.. We made a mistake when we call simplify once at every optimization step and we shouldn't do that. Because that changes the meaning of like upcast access to if you do upcast access one beforehand and access one disappears.

##### **Chenyu** [[00:31:37](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1897)]
Yeah. That logic is also before my time. So I know they're really told about it.

##### **Geohot** [[00:31:42](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1902)]
It's bad. It wasn't well thought out. If we fix that, there's a path to only do lets at the end of the opt-ops stuff. Is it worse? I don't think so. No, I think changing that is the first step. And then you can apply the opt-ops in parallel. Right now the opt-ops are inherently a serial process. There's always going to be some serialization on the same access, but there's just no way right now to.. it's just such a poorly specified space. We clean up the space and then also opt-ops should be able to apply to.. right now all opt-ops basically apply to the sink. This is wrong. You want opt-ops like unroll to apply to the reduce, not to the sink.

So then you can individually unroll the different reduces. How about reshape? What do you mean reshape? Reshape merges two together and redistributes. Well, so your views all need to be pushed to the outside. Well, there are limits for say if your numbers are too big for the hardware that you can specify for each. For example, what do you mean?

##### **Chenyu** [[00:33:14](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=1994)]
So there are things in the lower that shape and split one dimension to multiple because of how implementation.

##### **Geohot** [[00:33:28](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2008)]
Oh, I already separated that. That's sort of separated out the mapping. The mapping of the ranges to GPU should be like the last thing we do. I already separated that out.

##### **Chenyu** [[00:33:40](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2020)]
But what if you need to do more stuff, things like really change the compute?

##### **Geohot** [[00:33:52](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2032)]
I don't understand what you'd have to change. Split one global into two. For what? For the GPU thing?

##### **Chenyu** [[00:34:09](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2049)]
Yeah, for the GPU because the size is..

##### **Geohot** [[00:34:12](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2052)]
Yeah, if you're just doing that for the GPU, you can do that literally at the last minute. You don't need to do that in the kernel API. That's already removed. I moved all that to later. Okay, so if you have a range that's too big and can't fit in your global dimension and you want to split it across two global dimensions, when you remap the ranges to specials, you can just map them however you want. It doesn't matter and then run sim again and it'll clean up whatever things there are. Okay, this is already dealt with. The GPU thing should be dealt with at a completely different layer of abstraction than the ranges.

##### **Geohot** [[00:34:52](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2092)]
Okay, sounds good. Moving on, and now per Flama. I will make something like trans 7 8v model this week.

##### **Chenyu** [[00:35:14](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2114)]
I was still reading all the datasets stuff.

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2117)]
Sweet.

##### **Geohot** [[00:35:21](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2121)]
I would try to install Nemo and see if I can just use that for dataset.

##### **Chenyu** [[00:35:30](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2130)]
Or at least I have a way to know my implementation is correct. So what happened is Google tried to submit their LLaMA 405B by the remover. And I think that the implementation is not a complete completion. And I think partly is because they didn't upload any of the implementation details for how do they get the sequence to become individual training examples. That was annoying for me. I don't have a reference and they also don't have a reference and I suspect that maybe they realized that's why they got different convergence.

##### **Geohot** [[00:36:06](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2166)]
So we have to find it and we have to find it in the Nvidia code.

##### **Chenyu** [[00:36:12](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2172)]
So it's more of I also want to get something to run. So at least we can start to improve the runtime. I'm pretty sure how we impact or mask or token has very little impact on the kernel speed. So I also want to get that working. But yeah, for us to hopefully do this benchmark, we want to match how this data is packed together. So if I can find a way to import Nemo and also get that data, I can also work with my thing. Because there are apparently many weird strategies they use when they generate that data. So I think some of us disable. I don't know if all of us disable, but if it really calls into implementation details in how they pack sequence into one, I don't really see us replicating everything correctly.

##### **Geohot** [[00:37:13](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2233)]
Yeah, I mean, I don't know, like almost what I would do is just kind of, yeah, like hack the Nemo stuff to just.. How big is the dataset?

##### **Chenyu** [[00:37:20](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2240)]
A few terabytes.

##### **Geohot** [[00:37:24](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2244)]
I think everything fits into memory. Fits into memory. You can fit a few terabytes into.. No, it's like to put your device something.

##### **Geohot** [[00:37:37](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2257)]
Yeah, but no, yeah, I'm gonna put that memory area.

##### **Chenyu** [[00:37:41](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2261)]
No, I guess if you're able to sample and really just pick a random place and read it, then you really want everything to be in memory.

##### **Geohot** [[00:37:50](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2270)]
No, but there's no way I'm loading two terabytes into memory.

##### **Wozeparrot** [[00:37:54](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2274)]
You can also shuffle on disk.

##### **Chenyu** [[00:37:58](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2278)]
Yeah, there are 10 files on the disk.

##### **Wozeparrot** [[00:38:03](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2283)]
I mean, you could shuffle on disk and then just read sequentially.

##### **Chenyu** [[00:38:06](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2286)]
So I have, what, I have like a million IOPS? No, no, you cannot shuffle and then read sequentially, right, because then you already decompressed your data, there to be a thousand times bigger.

##### **Geohot** [[00:38:22](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2302)]
But I don't even understand, these drives have like a million IOPS.

##### **Geohot** [[00:38:28](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2308)]
How many samples am I using per second? A thousand? Yeah, with this I need 8,000 samples per second. Any SSD can do that. Any SSD can handle 8,000 reads per second. Okay, maybe that's why.

##### **Geohot** [[00:38:58](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2338)]
Yeah, no, I'm sure we got it. We got to just figure out how to leave it on disk and how to just pull the things off disk that we want. I don't think 8,000 should be a problem. If it was 800,000, okay, that's more of a problem. Then maybe we have to think about RAM. Yeah, we're trying, we're trying to test one. So that's probably fine. Cool. I mean, we're doing so much processing on each one of these data things.

##### **Geohot** [[00:39:20](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2360)]
I can't imagine this being.. Okay, anyway, let's move on to this. If you are saying stuff, I cannot hear you. You hear me now? Yes.

##### **Qazalin** [[00:39:54](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2394)]
I'm actually tiny device. You can see in the timeline on the top, just a Python timeline. And this week, I think I'm going to merge some ways to track buffers. So there's a good paper on this where it actually goes into details about how memory is scattered between activations and model state and stuff. So I'm going to try to figure out a way to visualize that.

##### **Geohot** [[00:40:30](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2430)]
The tiny device looks great. Sorry, go ahead.

##### **Qazalin** [[00:40:44](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2444)]
Yeah, so for LLaMA memory, right now, we see that the optimizer states just stay alive like 40% of the time. And that's not really much of a useful graph to be honest. It's the exact graph that we talked about, of like these steps and stuff. But I'm thinking of a different way to view this. Because I think it will be inevitable that you have a baseline of the model state and your optimizer and everything else is just how you can optimize your intermediate usage.

##### **Geohot** [[00:41:23](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2483)]
So I would really avoid, in the spirit of end to end, I would really avoid labeling weights as a certain kind of type. I would ask instead what, like almost like physics based characteristics do these weights have. So there's definitely a clear distinction between short lived weights and long lived weights. So there's buffers that only live during the execution of the graph, and there's buffers that persist beyond the end.

##### **Geohot** [[00:42:02](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2522)]
Should I be about that?

##### **Qazalin** [[00:42:04](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2524)]
Multiple schedules. Yeah, multiple steps.

##### **Chenyu** [[00:42:07](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2527)]
Yeah, like for your model weight or for your optimizer state. Those persist across each training step, for example. But gradients are not. You can, all the gradients of this step can disappear at the end of this step.

##### **Geohot** [[00:42:26](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2546)]
And if needed, they can be regenerated, create a new buffer for the next one. Similar to activation.

##### **Geohot** [[00:42:40](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2560)]
Yeah, I think that's a good distinction. I mean, I think it's that same distinction, like however we decide this, we want it to be the same way the memory planner decides it too. I'm also, so I see here in the tiny device, I'm seeing like get program for E3. Could we actually see the rewrites? No, no, no, that's not what I'm saying. I'm saying like in the timeline, it's just a big thing called get program. But that's going to be a whole lot of different rewrites, right?

##### **Qazalin** [[00:43:20](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2600)]
Yeah, you want to see the rewrite steps.

##### **Geohot** [[00:43:23](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2603)]
Yeah, I mean, it'd be cool if it was like a hierarchy, like you have get program at the top and then here are the 10 rewrites that went into the program. And then when you click on the rewrite, it actually jumps to that rewrite in the thing. But it's really good already how I can click and it goes to the thing. This is a place where tinygrad is way ahead of everybody.

Like, imagine seeing this for LLBF. Sorry, but let me see. But yeah, so I'd like to see underneath these get programs, I'd like to see it showing me all the different rewrites that happen. I also see like a get program taking 647 milliseconds. Is it really? That's crazy. I wonder what rewrites are taking so long. You know, this is very exciting. Yeah, add the rewrites and then..

Yeah, so I missed what you were saying about the, you have a paper that was talking about what the different types of parameters were.

##### **Qazalin** [[00:44:42](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2682)]
Yeah. So right now we have the buffer graph, but there's not actually any label of what this buffer actually is or how it's used.

##### **Geohot** [[00:44:57](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2697)]
How might you get that label?

##### **Qazalin** [[00:45:01](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2701)]
I trace it back to the kernel and I get the kernel metadata.

##### **Geohot** [[00:45:07](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2707)]
Cool. Yeah, I mean, that seems nice. The whole handling of metadata right now is a little bit janky. Like a better handling of metadata that can show almost like the line that triggered.. Okay, where's the line that triggered this compute? Where's the line that triggered this buffer creation? Any of that stuff that we can trace back is great.

##### **Qazalin** [[00:45:31](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2731)]
Is it back to realize?

##### **Geohot** [[00:45:35](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2735)]
I mean, even better than the realize, right? I guess there's both, right? There's where the specification happens and then where the compute happens.

##### **Geohot** [[00:45:50](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2750)]
I imagine one leads with the other.

##### **Qazalin** [[00:45:55](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2755)]
Can walk the trace back?

##### **Geohot** [[00:45:59](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2759)]
Yeah, but you know, I think you're making good progress here. I really like the tiny device. So yeah, we can play with it and just make sure whatever it is stays performant. My theory about the main reason people don't use profilers is that they're not performant, that they have way too much overhead. If there's a profiler that's basically free.. Oh, and they're too hard to run. But if you have a profiler that's basically free and runs with a single environment variable, that's great.

But yeah, okay, so you want to be able to click these buffers and see what kernels use them.

##### **Qazalin** [[00:46:47](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2807)]
And that's one possible direction and the possible direction is like the cache information, like the physical information about how..

##### **Geohot** [[00:47:02](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2822)]
Oh, like what the actual physical address of the buffers.

##### **Qazalin** [[00:47:07](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2827)]
I mean, so I saw these tools from AMD that they have. It's pretty janky, but it works. I think it shows you about when you have a memory allocation, did it hit the L1, did it.. How many times did it hit the L2.

##### **Geohot** [[00:47:27](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2847)]
Oh, yeah, I mean, yeah, if we can start.. There's been a bunch of those posted in the channel. The ones that show, Nvidia has a profiler for this to show you the usage of each bus. I mean, the main problem with using those things is they're super hard to run and they kill performance.

But I don't think that's inherent to the things. I think it's just bad implementation.

##### **Qazalin** [[00:47:57](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2877)]
Good.

##### **Geohot** [[00:47:59](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2879)]
Looks nice.

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2881)]
Preferably this channel. Okay. Moving on to drivers.

##### **Nimlgen** [[00:48:14](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2894)]
Yeah, so we've been working on the NVPCI. So now we have huge pages and performance is.. So sometimes it's better than the NV, sometimes it's worse. So, yeah, I mean, it's better in most cases when it's around the single device. Sometimes, I mean, the numbers say a bit worse because of the queue time. So I'll check this. So in general, the GPU speed seems to be good. Great. Do we have 5090 score? Not yet. So, yeah, so the next step, I'm just going.. I've been doing several cleanups for 1390. So, yeah, this is.. So actually this week I'm going to.. Yeah, so the primary goal is just to train some BERT and maybe some other networks to just make sure it's stable for like four weeks or so and merge it in CI. And yeah, and 59.

##### **Geohot** [[00:49:37](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=2977)]
Cool. So, I see this change here to the system.py and you use NVPCI. So this is for large pages. We do this. I see you doing this like two shift left 20 if size is greater than 8 shift left 20. Sorry, what? Sorry, the NVPCI one.

##### **Nimlgen** [[00:50:19](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3019)]
Oh, this one. No, actually, I've already merged this. We had it. So this part I merged. I mean, we had it for NV as well. So basically that helps to.. The difference in hardware between AMD and NV is that AMD can feed different.. And like in TLB they can have different sizes, like which has a power of two, like 4K, 16K, 8K and so on. And this importantly, I mean, sorry, NV supports only like the page size in the TLB, like 4K, 64K, 2 megabytes and so on. So because of that, yeah, we just need to align the size. And because the TLB allocation could be a lot of small pages like 4K pages, and because of that we just overalign this size to allocate it as one huge page like the TLB. That makes sense.

##### **Geohot** [[00:51:24](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3084)]
So AMD's.. How can you have a TLB that doesn't match the page size? Yeah. But how, I mean, how does it.. Like what if it sees contiguous pages that like merges them or something? No, there is a flag in the page table. Oh, that says like these four are one TLB entry.

Interesting. I've never seen that before. It looks cool. Yeah, seems like good progress.

Excited to have 5090 support. And then what we should do is we should add two of the H machines to CI. I think maybe instead of removing it from the.. Well, I don't know. It's up to you if you want to remove from the green boxes, but I think adding two of the H machines and always having neither of the drivers inserted on them is a good idea. They do have 5090s though. But yeah, then we can test the 5090 driver and test the 9070XT driver.

Can we, can we DMA from my AMD card to another? Yeah, I think we can. All right, that'd be cool. I think that's a.. So go ahead. I think that'd be a great thing to test in our CI, right? I think that like, you want to get to stuff that no other driver would dream of doing. It's that we are going to be able to DMA directly from Nvidia to AMD.

##### **Chenyu** [[00:53:01](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3181)]
Who's doing that?

##### **Geohot** [[00:53:03](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3183)]
I don't know. We are. Cool. I mean, but no, it's not just that it's cool. It's also like it shows that there's a framework. I mean, I want to start using the same framework for NVMe drives, the same framework for network cards. We can actually DMA across these heterogeneous devices and not have to use something called NVDirect or whatever it is.

##### **Chenyu** [[00:53:24](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3204)]
Great.

##### **Chenyu** [[00:53:27](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3207)]
You said it's faster for single GPU, or multi?

##### **Nimlgen** [[00:53:38](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3218)]
So it's also faster. I've tested the ResNet from the CI, which is not being installed, so like a few percent faster there. I mean, but yeah, it's a bit slower running LLaMA and actually the GPU times are the same or faster, but then queue time is a bit higher. So yeah, that's something to look at.

##### **Geohot** [[00:54:04](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3244)]
So what I want to get to for this is I want to start moving the implementation of our drivers into tinygrad. Like it should be a CPU tinygrad kernel to do all the updates and not Python code anymore. Well, we started doing it. You did this with how we do the symbolic stuff. But yeah, the eventual dream is that these HCQ drivers themselves become written in tinygrad. And whatever stuff is going to require to do that. But imagine also being able to run them on a GPU. Or imagine being able to have just a tinygrad kernel that does the enqueue. So like GPU2 can enqueue your kernel on GPU1 or maybe even on itself.

But yeah, that should fix all the enqueue times I think too. Like it's just some compiled C code. So I'm going to.. Anything else for the driver? No, I'm moving on to vote. Still, follow system progress. Better, I'm hoping to have something deployed this week and start getting it. I think my main issue right now is there's a separation between chunking, like passing a chunk and then storing it. Because I think currently we assume that all machines that run compute have drives. I don't think we have to.

##### **Wozeparrot** [[00:56:09](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3369)]
Yeah, because then we have the issue of, okay, we send a recent in the chunk twice then.

##### **Geohot** [[00:56:16](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3376)]
Oh, you're saying like what happens if we hash it in a different place from the drive. I would guess that the machine that does the hashing is also the one that does the store. Yeah. Which is, yeah, I'm okay with that. I'm okay with assuming that all machines that have drives have compute.

##### **Wozeparrot** [[00:56:31](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3391)]
Okay.

##### **Geohot** [[00:56:33](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3393)]
That's totally fine. We can assume that stuff. And then also we should think about how to run a local version of this file system. Like I want to switch cache downloads over to a local version of..

We can have locally, we have the same block store.

##### **Wozeparrot** [[00:56:52](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3412)]
It can be hashed in the same tree.

##### **Geohot** [[00:56:55](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3415)]
Yeah, good enough. Yeah, I think that's all we care about. Yeah, I think we don't even.. I guess, yeah, we don't even really care about how the files are stored.

##### **Wozeparrot** [[00:57:00](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3420)]
But it's the same tree and then you can hit the same hashes from the cloud or from locally. It's okay.

##### **Geohot** [[00:57:07](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3427)]
Yeah, yeah. And like, yeah, ideally it should all just be like.. It should be like a redo cache, like it should be like a.. Like the only way to access things in tinygrad's download should be by the hash.

##### **Wozeparrot** [[00:57:30](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3450)]
Okay. How do we download something into, like if a user wants to run some new LLaMA model. Well, I'm not the pre-downloaded.

##### **Geohot** [[00:57:41](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3461)]
No, I'm saying like sure you can keep around the helper methods, right, you can keep around fetch and keep around from URL. But under the hood what that should do is not stick it in cache downloads. It should stick it in the local tinygrad file system.

##### **Wozeparrot** [[00:57:55](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3475)]
But then how will the user specify that they want.. Like from URL is you're providing a URL. Yeah, then do they also provide the hash?

##### **Geohot** [[00:58:06](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3486)]
Can you store that in the SQLite if you want to store that in something?

##### **Qazalin** [[00:58:11](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3491)]
Okay.

##### **Geohot** [[00:58:12](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3492)]
Yeah, we can store a lookup in something. I guess we lose that lookup after we download everything, kind of sucks.

##### **Wozeparrot** [[00:58:20](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3500)]
I don't think we'd be downloading everything we compute.

##### **Geohot** [[00:58:23](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3503)]
Yeah, my only point with this is that I want to make sure that if they do a from URL, however that works in the backend, if they then do a from hash on the same thing it also works. Yeah, that's the exposed requirement to this.

From hash and from URL should use the same backing store. Yeah. You can also just hash the file and store the hash to file local.

Oh, like as a file. Yeah, that works. Yeah, maybe that's the way to do it. Just keep the download directories, just be kind of like instead of the file containing the data, it contains the hash.

Yeah, just whatever you just wrote. Well, this was great. 10% overhead both in the bounty target also. I have to know what device is on what host. Yeah. And just currently our device specification.. Is it like getting a group ID to ops device.

Oh, yeah, I mean, there's no reason that ops device is kind of this.. Yeah, I think the colon thing is kind of bad. Yeah, you need a better way to specify more complicated topologies.

##### **Wozeparrot** [[01:00:08](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3608)]
Yeah, yeah, yeah, I'm kind of don't have that right now.

##### **Geohot** [[01:00:11](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3611)]
Totally okay. I mean, maybe the first thing to do is to have ops device have that number after the colon be a constant put. And then you can have multiple, right, like sources can be as many counts as you want and that's just a topology.

##### **Wozeparrot** [[01:00:25](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3625)]
Okay.

##### **Geohot** [[01:00:27](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3627)]
Like every final thought. And so instead of having an explicit thing called group, you can just have, yeah, the first refactor would be getting rid of the colon. And then having that be a constant and then there's no reason that you can't support three constants if you want a 3D topology. I don't know, but you also want to have the idea of a max.

I don't know if the device should include the world size. Yeah, maybe should. Yeah. I'm kind of referring to that. Moving on to Alex. A deep complaint because Alex is still not in any proper.. Yeah, let's do it. Let's move it in.

##### **Chenyu** [[01:01:29](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3689)]
Oh, yeah, there was a change on next runner to take file as input and like out on the benchmark release, low more than 100% slow.

So, welcome.

##### **Geohot** [[01:01:51](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3711)]
You speak more about what else is needed to move on next to tinygrad proper. Other than like count. You mean me? No, I'm asking. Yeah.

##### **Chenyu** [[01:02:18](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3738)]
Maybe not for this meeting, but I'd like to know what, because we fixed a bunch of stuff already, right, so want to see, other than maybe some cleanup for general styles and functions, I'd like to see what other blockers are there so that we can have automation for.

##### **Geohot** [[01:02:47](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3767)]
Before you want to make this happen faster, is there a way..

##### **Chenyu** [[01:02:54](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3774)]
Okay.

##### **Geohot** [[01:02:56](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3776)]
Okay. Some symbolic stuff for us, like us. Hi, can you hear me? Yes.

##### **Sieds Lykles** [[01:03:11](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3791)]
Yeah, so I updated the PR that George had merged this week and then reverted. And it is now also reducing the right output. Basically what happened is I fixed one bug and then there was another bug. It was like, that was a sign and so after fixing the first error, I decided to produce the wrong output which..

##### **Geohot** [[01:03:41](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3821)]
Yeah. Fixed now.

##### **Geohot** [[01:03:44](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3824)]
If I merge 1188, this is fixed and has a test.

##### **Sieds Lykles** [[01:03:51](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3831)]
Yeah, I mean, I was just using a squashing made unit test from that couldn't run the actual LLM app. So I just use the unit test and the unit test is fixed.

##### **Geohot** [[01:04:07](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3847)]
Why couldn't you run the LLM app?

##### **Sieds Lykles** [[01:04:12](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3852)]
I don't know, just use the LLM memory.

##### **Geohot** [[01:04:17](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3857)]
Well, that doesn't sound good. But yeah, no, unrelated. Cool.

##### **Wozeparrot** [[01:04:20](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3860)]
Wait, is it only a 1B model?

##### **Geohot** [[01:04:22](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3862)]
It's a 1B model, but it does use a lot of memory. Oh, it might be the context size being crazy big too. I don't know. But cool. Great. I'll merge this. Looks good.

##### **Sieds Lykles** [[01:04:32](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3872)]
I think it's more like how to notice that SteelBiff is incorrect for uOPS. Like, it's only the helper, like SteelBiff helper, is only correct for int and not for symbolic. So I think if stride is not, it might produce problems.

##### **Geohot** [[01:05:08](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3908)]
I mean, what we really want, and I think what a lot of your project is going to be, is going to be just thinking about all these cases and just fixing them. Like, we need to support arbitrary symbolic. What I want to do for the LLM app is I want the T, like the number of tokens, I want that to also be a variable.

##### **Sieds Lykles** [[01:05:28](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3928)]
Yeah. Yeah, I don't think there's a further for the shape tracker. But I don't think it works with variables.

##### **Geohot** [[01:05:39](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3939)]
Yeah, I don't think it does. I don't think it does at all. I mean, in theory, what we should be able to do is just like anything should be able to become a variable and it should still work.

##### **Sieds Lykles** [[01:05:50](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3950)]
Yeah.

##### **Geohot** [[01:05:51](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3951)]
So, yeah, I mean, that's kind of the test, kind of the direction to go here. Okay. Anything else?

##### **Sieds Lykles** [[01:06:10](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=3970)]
Yeah, going to like working more on the new fuzzer. And like now, I'm using the bitfactor fuzzer, which also does sort of overflow behavior. And like there's some current, like there's some, we can't really have an any quarter to like a less than comparison. Right now that might just get forwarded to a true or false, whereas if one side of your comparison can overflow, then it's not actually constant. Yeah.

##### **Geohot** [[01:06:52](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4012)]
So I see. Sorry, go ahead.

##### **Chenyu** [[01:06:57](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4017)]
Overflowing is just implementation details.

##### **Chenyu** [[01:07:01](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4021)]
It's like having the number overflow. It's pretty much always not an intended behavior. Unless, I don't know if people do increase the stuff for uint. Maybe people use the wrap around for uint for other stuff. But for signed integers, for floats, I can imagine a float doesn't have this problem. So maybe just int.

##### **Geohot** [[01:07:26](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4046)]
I don't think people use this as an intended behavior. Maybe that's fine. Because when we start to come..

##### **Chenyu** [[01:07:39](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4059)]
When we start to consider overflow in these min, max, and more math formula stuff, that's a lot of your implementation details of those dtypes.

##### **Geohot** [[01:07:53](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4073)]
I mean, what we might want to do for this, and we used to have something like this, is we just might want shapes to not be int32s. We might want them to be arbitrary integers. I think we used to have something for this, but it was taken out because it was slow. But they should just be arbitrary precision integers. And then there can be a pass later on, which puts them in real dtype.

##### **Sieds Lykles** [[01:08:14](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4094)]
I guess my problem is that I'm.. The fuzzer is going over each rule in symbolic one by one, generating random uops. And some of the uops are not equal before and after the simplify because there's some overflow.

##### **Chenyu** [[01:08:39](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4119)]
Yeah, I think for the actual ALU we have a pass that can judge the dtype for the number, int32 to 64, if it surpasses that.

We still have it. I think we should have it.

##### **Sieds Lykles** [[01:08:56](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4136)]
Yeah, but I mean that's only for integers in like..

##### **Chenyu** [[01:09:04](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4144)]
Yeah, but I think let's look at the intended behavior. Right. So if you say the fuzzer finds the numbers, lets intermediate or outputs overflow, the actual intended behavior is to change the type so that it doesn't overflow. It's not like we want to make the overflow behavior the same.

##### **Sieds Lykles** [[01:09:28](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4168)]
Yeah, okay.

##### **Geohot** [[01:09:29](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4169)]
Okay, I'll move on with that. Yeah, because otherwise we're starting to use our files.

##### **Chenyu** [[01:09:42](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4182)]
Yeah, we really don't want in the, like, the master rewriting rule to start to consider, okay, what if this overflows. It's already annoying to have None and zero and.. Thanks.

##### **Geohot** [[01:09:59](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4199)]
Well, yeah, then what we might want to be using is again, this arbitrary precision dtype. And it's almost a question if we only want the symbolic rules to apply to this arbitrary precision dtype.

And we can do all the shapes and the indexing in it. I mean, there's not like that in his own either, rosewood by comparison operators that are building problems. Most of them are not fine. Thank you. Yeah, I think the..

##### **Chenyu** [[01:10:50](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4250)]
On the mental thinking would be if it's something that has an intent to use case that a user will want to happen and we track close. If it's just the way we run fuzz or benchmark and it's really trivial, then don't change the core properties of dtypes for something because of that.

##### **Geohot** [[01:11:15](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4275)]
Yeah.

##### **Qazalin** [[01:11:17](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4277)]
Yeah.

##### **Geohot** [[01:11:19](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4279)]
Yeah.

##### **Chenyu** [[01:11:23](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4283)]
Let's quickly go through other counties. I see Flata, you have anything to add for writing on it.

##### **Flata** [[01:11:33](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4293)]
Yeah, so I finished the rewrite. I did find it slower for now, so I'm trying to debug where that is, but I kind of want to do the correctness check. So I'll probably just run the eval script and make sure that the accuracy or discord matches with the existing one. I still have to.

##### **Chenyu** [[01:11:52](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4312)]
I'm ready for slow one.

##### **Flata** [[01:11:57](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4317)]
I think there is, I think like two for loops right now in the current implementation on numpy. I don't know. I started commenting out code just to see where the slowdowns are. I did it as well. I think only the main post process. So I think the other ones I saw how to modify it so that it can be jittable because it needs to use the variable as well. You need to be a variable number for some of them as well.

##### **Chenyu** [[01:12:27](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4347)]
Okay.

##### **Flata** [[01:12:29](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4349)]
Yeah, I'll probably write a better writeup once I understand where the slowdowns exactly are in this case.

##### **Chenyu** [[01:12:38](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4358)]
I think these experiences are very important for anygrad development because they certainly link to how easy other people can rewrite existing stuff in tinygrad. So anything you find, if you can write even just for the things you encounter, if you find any inconvenience or anything you think the framework is not doing great for your development, that would be good to know.

##### **Chenyu** [[01:13:04](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4384)]
Okay. Sounds good.

##### **Geohot** [[01:13:08](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4388)]
Oh, we have a bunch that removes all the realize in certain item. Did someone submit for that? No. Oh, yeah, I mean, that'd be a great one. I also really want to remove that realize in the KV cache too. I think now we have a really good understanding of what assign is though, which is exciting. Like we used to just have assign and it was this nightmare and no one really knew what it was. But it's just store.

##### **Chenyu** [[01:13:35](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4415)]
For your test, how do you envision the final single kernel look like?

##### **Geohot** [[01:13:43](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4423)]
Which test?

##### **Chenyu** [[01:13:44](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4424)]
So you write a range of size 10 and you say for i equals to English and the ith element is assigned to i. Yeah. How do you think the final kernel looks like?

##### **Geohot** [[01:14:01](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4441)]
Oh, I want to look at what I wrote again. I remember the test, that item loop. Oh, I just imagine it being literally just that, literally just 10 stores, each to the element. Yeah, it's not a for loop. No, no, no, the kernel obviously wanted for loop in it. The kernel is just going to have 10 stores in it. So it's going to be.. Yes. Like it's just going to have, OK, so passes in some buffer and the buffer has like buf[0] = 0, buf[1] = 1, buf[2] = 2.

It's not going to extract the for loop or anything. Yeah, that's.. How do we write kernels like that now? We have a single kernel, stores to different parts of.. It's not done correctly now. I know how to do it. It's the problem. Yeah.

##### **Chenyu** [[01:15:24](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4524)]
So because for now we only support kind of two types, right, when this store everything inside that buffer. Yeah, we don't, or take a slice of that in the outer world and kind of store into that slice.

##### **Geohot** [[01:15:40](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4540)]
Yeah, this is both the wrong way to do it. So you don't need to do it in the outer world. You can do it in the inner world. And what the inner world will be is that kernel will basically become a lot of load, store, load, store, load, store, all put in one kernel. And then it'll realize that the load stores are irrelevant in all places except i and it'll just get simplified down.

We already do have logic for this. We already do have logic where if you're doing a load store and they're in the same place, then it just avoids it. This doesn't go. I see. Cool.

##### **Chenyu** [[01:16:22](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4582)]
Okay.

##### **Chenyu** [[01:16:23](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4583)]
Other bounty. The reflector ones I was against, anything that's ready for review, other land. If you want to try the CIFAR was torched.

##### **Geohot** [[01:16:37](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4597)]
Oh, yeah, sorry. I was going to try that last week. Okay. I'll do that this week. I did the other one though. Yeah, so I think that's it for this meeting. We're excited, over time because we were discussing all their stuff. We have torch boys. Com is coming to me now. Great.

##### **Chenyu** [[01:17:10](https://www.youtube.com/watch?v=DSWQCT9mypQ&t=4630)]
Okay, that's it. Thanks everyone. See you next week. Bye.
