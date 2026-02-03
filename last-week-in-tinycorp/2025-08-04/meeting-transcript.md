# 2025-08-04 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
company updates
rangeify, flash attention
mlperf LLaMA
viz tool
drivers
cloud
onnx
other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=jH9ra0-bRiw)

### Highlights

- **[Company Update](#geohot-000008)**: More tiny boxes are being produced and shipped. A special order of computers is being built for the "Kala project," with Tinycorp handling part selection and purchasing.
- **[Rangeify and Flash Attention](#geohot-000108)**: Geohot introduced a new concept called "rangeify" that pushes indexes through views instead of the views themselves. This allows for more granular control over memory and computation, enabling Flash Attention by creating intermediate buffers only for mismatched axes. The long-term goal is to replace the `ShapeTracker`, apply this to the entire computation graph, and enable expressing complex operations like RNNs with O(1) memory.
- **[MLPerf LLaMA](#chenyu-001036)**: The data loader is ready for MLPerf LLaMA training. A key challenge is the high memory usage (20x model weight vs. an ideal 4x), which is a separate issue from rangeify and relates to long-lived activation buffers needed for the backward pass. The team has nine weeks until the submission deadline.
- **[Viz Tool](#nimlgen-003913)**: Nimlgen reported performance issues with the visualization tool on large BERT/LLaMA runs, where it becomes unusable and fails to display collected kernel data. Qazalin will investigate the bug.
- **[Drivers](#nimlgen-002711)**: Nimlgen is working on stability issues for both NVIDIA and AMD. On NVIDIA, the 5090 card sometimes hangs on PCI reset, possibly due to a driver collision that has now been addressed. On AMD, the MI350X still has stability problems with BEAM, and AQL support is likely needed to reduce kernel sync overhead.
- **[ONNX](#chenyu-004250)**: The ONNX parser integration into `tinygrad` is nearing completion. This includes support for new instructions required by models in the ONNX Model Zoo.
Of course. Here is the corrected and updated "Other Bounties" highlight with timestamps for each item.
- **Other Bounties**:
    - **[Reduce Axis](#chenyu-004405)**: B1tg is working on removing `shape==1` from reduce axes. The generated kernel's functionality should remain the same, though minor source code differences are acceptable.
    - **[Stable Diffusion Training](#geohot-005029)**: Hooved estimates a 32-hour training run to meet the MLPerf target and was given the go-ahead to start the full run.
    - **[Muon Optimizer](#geohot-005636)**: Geohot requested that the PR for the Muon optimizer be cleaned up, with minimal diffs and proper asserts for unsupported flags, emphasizing code quality for user-facing features.
    - **[Whisper](#chenyu-005914)**: The bounty requires getting Whisper running in WebGPU and matching the OpenAI reference quality; additional model quality explorations are not required.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=0)]
We got people, we got a small meeting, so let's get started. Let's start with company update.

##### **Geohot** [[00:00:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=8)]
More tiny boxes are being made. We shipped two out last week, got like five. Some of them don't work. I'll fix them. Then the project for Kala has been taking a lot of time. We're building the computers for Kala project.

##### **Geohot** [[00:00:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=37)]
That's coming along too. Kala has made a special order with Tinycorp for some computers that we've been working on.

##### **Chenyu** [[00:00:47](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=47)]
Make a special order and it's kind of also built by Kala? Yeah, Kala does the building.

##### **Geohot** [[00:00:54](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=54)]
We did all the part selection and purchasing.

##### **Chenyu** [[00:01:01](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=61)]
Okay. So I think the big thing is Rengify.

##### **Geohot** [[00:01:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=68)]
Yeah, so what I realized was, like, you don't need to push views.

##### **Geohot** [[00:01:19](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=79)]
The only thing you care about doing is indexing in the appropriate places. So you can actually just push indexes through views. And the only thing you care about doing is indexing in the appropriate places. The way to think about this is more that it's split. Like, if you think about a kernel, if you think about the axes of a kernel, you can split the axes of a kernel horizontally. So you can do some things only on a few axes. You don't have to do.. Imagine you have a whole model and you want to take the batch out of it. You can do this. You can completely separate the whole model. You can completely separate the range for the batch from the entire rest of the model at inference. And you can't do this if you're doing, like, normal view pushing kind of stuff. There's no amount of view pushing that's going to.. Yeah, that's the simplest case and the case that I focused on that I think leads to, like, all of them. So if you're running a model and you wanted to run the model on.. It's at inference and you're running the model on 10 examples. Imagine the difference between running all 10 at once, versus running a loop, running one example in each one of the loops. So you need 10x less memory in order to do it like that. But you're also going to have, in the limit, 10x more axes to your weights.

##### **Geohot** [[00:02:46](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=166)]
So that's the tradeoff.

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=167)]
You're trading off locality for.. Well, in that case there's no recomputation. In that case the computation is the same. But there's places where you can trade off.. and, like, recompute instead of storing. So that's what flash attention is. When you get to a point where a node has two children.. So we've always had this problem when a node has children, and the children have different views. What do you do? You can't push the view. There's no way to push view. So we would have to just insert a contiguous there. But, again, the range-of-eye insight is that contiguous doesn't have to mean contiguous on every axis. Like, a normal contiguous, what that means is end every range in the indexing and create all new ranges for the indexing. But if you do that, you're not going to get flash attention. You're going to get three kernels. So the old flash attention fuser would push the views anyway. You can push the views anyway. So if you have a child that has two different views, and you push the views anyway, what happens is all the parents duplicate. So you're going to get replications of the parents with the different views being pushed. But this is bad because now you're doing recomputation. So what range-of-eye finally lets you do is say, OK, I have two shapes of four dimensions coming in. The only axis they mismatch on is axis 3. I'm just going to end ranges for axis 3. And then when you end those ranges, that end range is actually a store followed by a load.

##### **Geohot** [[00:04:32](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=272)]
And that's your intermediate buffer. I believe that's completely generic.

##### **Geohot** [[00:04:40](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=280)]
I believe that also works for upcasting for locals. If you see that I pasted one of the upcasting things. Yeah. So I'm working on it now for reduces. The reduce right now that it's generating is,

##### **Geohot** [[00:04:59](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=299)]
is still, the reduce still has like a weird loop

##### **Geohot** [[00:05:09](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=309)]
because it's not expanding the register. It's not expanding ACC 0. But yeah, I can fix that. We can also think about changing the semantics of the reduce op to be, what Halide does is it creates the buffer. It creates the buffer. That you're going to reduce into. And then the size of that buffer can actually determine the, Which ACC 0 reduces. Which ACC 0 reduces. And you can still get rid of the ones at the end. You can have something like if you want to reduce, your inputs are like 16, 16. Your reduce into is 16, 1. And your output shape is 16. That's all totally fine. See, I still think we should get rid of the ones there. So yeah, I'm just going through and re-adding each of the optimizations to rangeify. Rangeify goes really far. You can delete the shape tracker now. Like there's no longer a need for views for the shape tracker. And I know it's like sad to like kill something that's existed for so long, but. Great. So, well, we can keep it alive and test and make sure that symbolic can find all the patterns. I don't know about that. We can keep it for a while maybe. Let's make sure symbolic can find any patterns that are important or any. Oh, I thought that's a precondition.

##### **Chenyu** [[00:06:30](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=390)]
It should at least match what's the precondition to remove it. Yeah, I guess.

##### **Geohot** [[00:06:35](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=395)]
But after that. Yeah, after that, then yeah, we can just delete it. Bye bye shape tracker. It's been nice having it. But yeah, we can just, we push ranges through views. And then the eventual goal of this is there's no reason this has to be done on the kernels. It can be done on the big graph. You could push ranges through the entire big graph. This gets into actually the user putting ranges on the big graph to specify things like.

##### **Chenyu** [[00:07:05](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=425)]
Gradient accumulation.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=427)]
Well, you can specify gradient accumulation. You can specify batching. You can. Stunning MNIST. Stunning MNIST. Yeah, you can specify the actual optimizer itself. You should be able to specify things that look like scans. Like RNNs.

##### **Geohot** [[00:07:26](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=446)]
You should be able to express RNNs with O of 1. Sure. Yeah. Are we getting this in a month?

##### **Geohot** [[00:07:35](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=455)]
We're getting this in a month? Probably about how long it's going to take, yeah. Yeah, I think, I mean, look, it took a while to figure out what the formulation should be. But it's not like I was doing nothing. I did a whole lot of refactors. Notably, define reg needed to be refactored the way that it was. And, yeah, I mean, all the way that I refactored reduce into load store. All of these things were completely in the right direction. I didn't do anything wrong. I mean, the wrong stuff was like shape tracker and views. But I think that was kind of hard to know at the time. We were so focused on this idea of a single kernel. But then you start realizing that you need to find solutions that, you know, will work for the entire graph. And then you realize that view pushing is not going to. You're not going to be able to push all your views all the way to the left of the huge graph. That's never going to happen. And then this also gets into the other thing that makes this all hard to move to the big graph is that we need some quick way to do, like, deduping. You don't actually want to reassign ranges to new areas if they're duplicates of other areas that it's seen already. So right now we do this with like, once we split it into kernels, like think about how few of the UOPs in the big graph actually end up in a kernel for a LLaMA. Because every time you're doing like 10 layers. So, yeah, I mean, the dream thing to do is to, well, I mean, we could also just write LLaMA to use ranges in the big graph. And then that fixes that explicitly. But you could also, if you could figure out how to do that implicitly, if you could figure out how to, how to re-extract loop semantics from a graph. Oh, hey, this is just that same thing repeated. Cool, I can just merge them together into a for loop. So, yeah, I mean, it's not like, yeah, so it's just, this has all been a completely steady progression looking back on it for the last two months. And it was going to the right place.

##### **Geohot** [[00:09:45](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=585)]
Great.

##### **Geohot** [[00:09:46](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=586)]
Yeah, and now we can generate, that thing is real flash attention. But I post it on Twitter. Do you need like a tensor core? You can. I mean, yeah, well, that's real. Yeah, I mean, the QK thing should be using tensor cores. Yeah, of course. But like, this is all. Structurally it's there. Yeah, yeah. I mean, tensor cores are an optimization after this. But yeah, there's no reason that it shouldn't be able to see that reduced small pattern and add tensor cores. And now that we have the like expands properly, like we can say, oh, this is actually expanded over this axis. That's cool. This is a tensor core.

##### **Chenyu** [[00:10:22](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=622)]
Great. Excited. You also need that for memory stuff. Okay, so let's relate to the next point. Wait, what? Oh, that's a different problem. Okay, that's a different.

##### **Geohot** [[00:10:34](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=634)]
Okay, that's a different.

##### **Chenyu** [[00:10:36](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=636)]
Okay, anyway, let's move on to MLPerf LLaMA. So, WordPerf is not here, but he did a bunch of work to pipe the data loader. So now we have a data loader that we can train. The MLPerf LLaMA. So for MLPerf, I just learned that in the upcoming rounds, so bird has been killed and replaced by LLaMA 8B. So there will be two LLaMA's, one for 8B and one for 405B. Our contract is on 405B. But AB is the new bird, although it's much bigger than bird. So now we can train that. You can see my drawing on the whiteboard in the LLaMA 8B. So I'm going to create a new LLaMA for 405B channel.

##### **Geohot** [[00:11:26](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=686)]
And I added some tricks like gradient accumulation and another PR for optimizer offloading to

##### **Chenyu** [[00:11:40](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=700)]
CPU, which we will need eventually for the 405B. We probably don't need that for AB, but we definitely need that for 405B. Does the test do the eval working? Eval is working, but now it's very slow. And Westbury will be working on that. Yeah, so it's less of an issue because for LLaMA, we don't even train over one epoch of the data. So training loss is very similar to the eval loss that you expect.

##### **Geohot** [[00:12:07](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=727)]
Yeah, but we're seeing training loss go down on AB. Like how long is it going to take? I know you put it on the board. Does that mean it trains or does that mean it finished?

##### **Chenyu** [[00:12:15](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=735)]
So that means it kind of runs with global bus size 32 and the loss is going down. Okay. Because.. But we haven't actually checked if it's converging to the right. So the initial random log perplexity is 10.5. It's basically just log of the cabs because it's like a nuclear cab set. The required target is 5.6. So it needs to be lower than 5.6. I trained a 1B for 24 hours and it lowered to 7.5-ish. And I thought it will go much lower because it's a 1B model. 8B model with a much smaller batch size is running now and I just checked it's like 10.1 after 10 hours. It doesn't seem right. No, but think about it. 405B model is seven days to go to Latin.

##### **Geohot** [[00:13:11](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=791)]
Yeah. So why is that not right? Well, I mean these things are in log space, right? Like even 7.4 is a lot. So initially it's a lot faster, right? Is that why you're.. Well, yeah, that's what I'm saying. Like I expected to come down from 10.4 to like 7 really fast.

##### **Chenyu** [[00:13:31](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=811)]
And then sure, I expect the difference between 405B and 8B to be more like 5.6 versus like 5.9. Part of the reason is 8B is training with a global batch size of 16 or something like that now. So that also contributes to that. The batch size we should be aiming for is like 1000. Got it. Okay. So the main problem here that I think is very important to how we can do to this contracts memory. We already had this problem before training BERT that we seem to be using a lot more memory than the.. So if we think about what's the bare minimum of memory we need to use, it's the weight, it's the gradient of the weight, it's the optimizer state of the weight. So it's like.. So two sets of LEDs. So it's roughly like 4x of your model weight. And now we are at, I think, 20x. So there's 5x of diff here that is either the intermediate states of some kernels because we generated.. Why we don't need, for example, flash attention if you just get three small input in and one small input out. Something like that. We don't need the intermediates. We don't need the.. There are definitely more places that, say, for activation, it's not clear if we are storing both end of the activation or just one end. And it's also not clear if we can just say we want to regenerate instead of.. Recompute instead of storing it for backend.

##### **Geohot** [[00:15:09](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=909)]
Yeah. So I'll warn you that rangeify is not going to address any of these. Okay. Rangeify is going to address two things. So even the flash attention thing. It depends what the backwards of flash attention looks like. Right. If it's just generating intermediate buffers and the intermediate buffers are only used on the forward, then that's not going to increase your memory very much. Right. Because it's going to be the same.

##### **Chenyu** [[00:15:31](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=931)]
No. It's more of allowing single kernel to have multiple reducing it. And if it knows that the intermediates are very big, you might as well just squeeze it into.. And don't generate intermediate power.

##### **Geohot** [[00:15:45](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=945)]
No. But I don't even think that's a problem. Right. Like anything that's persistent memory usage that's bad.. Yeah. Is when you have long edges. When you have long edges from the forward pass to the backwards pass. Yes. And that's the kind of thing that we have to look for. So any intermediate that only exists in the forward pass is not going to really add a sizable amount of memory. It's going to add memory bandwidth, but not memory.

##### **Geohot** [[00:16:14](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=974)]
Oh, yeah.

##### **Chenyu** [[00:16:15](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=975)]
What I mean is the older intermediates that result also in the backward pass.

##### **Geohot** [[00:16:20](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=980)]
Yeah. So this is.. And this is the kind of thing that we have to think about how we can build tooling for, build tests for. Right. Think about it like you're scrolling across the graph from left to right and you get to the loss. How many buffers are alive right now? Why are these buffers alive?

##### **Chenyu** [[00:16:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=997)]
Yeah. So technically, ideally, we should have a flag that says can force regenerate. Right. And then we can be making everything so there's like no long ranges and everything in the backward can be recompute. Well, yeah, I mean.. Yeah. So we should have that setting and then we can decide, okay, in which case it's better to keep the edge ending. Because we might.. It's kind of called like kernelized, you know, when you think about it, right? Yes. Because to some extent for the really big one, we can afford very little long edges. But anyway, yeah. So that's the.. I think that would be the main..

##### **Geohot** [[00:17:18](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1038)]
We have to think about like, yeah, how we want to specify that. Because we don't have the best tool. I mean, we should start out by having tooling to visualize this and then think about what we want the semantics to be. But this isn't range-fying. This is totally.. Okay. This is not range-fying. Yeah. So don't expect.. Great. This is a separate problem we have to solve. Great.

##### **Chenyu** [[00:17:36](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1056)]
Yeah. So for example, I wrote the optimizer offloading to a CPU. It kind of is working. Yeah. But it's really not that useful when your overhead is 20x and this only saves you like 2x. So yeah. We can start to optimize the speed for that transfer. That's for sure. But that's not the main technical difficulty now. Anyway, so I think I will continue working on this, posting what I think will be a good thing to add to the tooling. So in that way, we can iterate faster. Yeah. That's LLaMA.

##### **Geohot** [[00:18:15](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1095)]
We only have.. I don't know. How many weeks left? Nine? You put it that way. It seems like a lot of weeks. Yeah.

##### **Chenyu** [[00:18:26](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1106)]
We have nine weeks left and each training will take two weeks. So great. Yeah. Yeah. Okay. Enough gloving.

##### **Geohot** [[00:18:34](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1114)]
Let's move on to this.

##### **Hooved** [[00:18:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1117)]
Okay. So let's start with the build. So let's start with the build.

##### **Geohot** [[00:18:44](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1124)]
I cannot hear you if you are ridic– trying to talk. Hmm.. Don't think it– Is it recording? Yeah, yes.

##### **Qazalin** [[00:19:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1148)]
Okay, for some reason why I disconnected my headphones. Sorry. disconnect everything uh i merged an initial assembly analyzer in this with lvm still working on SQTT it's really hard to figure out what's going on uh but yeah making progress on that i have to like basically reverse engineer the binary format uh there's literally no docs

##### **Geohot** [[00:19:36](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1176)]
i could find about it yeah there's not isn't there some stuff that i saw linked that had some parsing for it

##### **Qazalin** [[00:19:49](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1189)]
it's just a blob like i have to either disassemble it and try to read it

##### **Geohot** [[00:20:10](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1210)]
host please

##### **Hooved** [[00:21:06](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1266)]
Thank you.

##### **Qazalin** [[00:21:17](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1277)]
Thank you.

##### **Nimlgen** [[00:22:02](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1322)]
Thank you. Thank you.

##### **Geohot** [[00:22:36](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1356)]
Thank you.

##### **Geohot** [[00:23:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1393)]
Thank you.

##### **Geohot** [[00:23:38](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1418)]
Thank you.

##### **Geohot** [[00:24:09](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1449)]
Thank you.

##### **Geohot** [[00:24:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1477)]
Thank you. Thank you. Thank you. Thank you. Thank you. Thank you. Great.

##### **Geohot** [[00:26:45](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1605)]
Cool. Great. Great. Great. Great.

##### **Nimlgen** [[00:27:11](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1631)]
Yeah. So actually, within VCI, we see two problems. One is the segfault, and the second one, I hope I fix it. I mean, actually, there is one problem with 5090 that sometimes it doesn't return after VCI reset. So I've never seen this. I can't recall this, the 3090, 4090. But if 5090 isn't shut down gracefully, so yeah, and you do the functional level reset, it won't return. And the only way is just to reboot machine.

##### **Geohot** [[00:27:58](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1678)]
AMD, there's a whole bunch of complaints about. I've talked about this with AMD, where AMD will keep up the PSP. They want to keep it up long term. I'm kind of scared that this is some security feature.

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1693)]
Oh.

##### **Nimlgen** [[00:28:15](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1695)]
I don't know, really. I mean, it's strange, because sometimes it returns fine, and sometimes it's not.

##### **Geohot** [[00:28:27](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1707)]
Is there any kind of lower level PCI reset?

##### **Nimlgen** [[00:28:33](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1713)]
Yeah, we can do bus reset. But I've seen the same reports with a hopper GPU, so that the bus reset also just doesn't help. Yeah, we can try to do that. I can try. We can actually try to update the firmware, but I think it's not the firmware itself. It's VUS or something lower.

##### **Geohot** [[00:29:00](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1740)]
It's super annoying. Yeah, I mean, it's super annoying if the GPU can get into some state that we can't reset it from, and that the only way to fix it is rebooting the machine. Yeah. Yeah, I mean, what I would try to do here is I would just spend some time trying to get like a repro of the crash. Like, can we get something that puts it in the bad state repeatedly? And then, okay, then we try to figure out how to get out of the bad state.

##### **Nimlgen** [[00:29:26](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1766)]
Yeah. I mean, simply. Yeah. Just not loading the GSP or just loading the some bad data with the GSP. Yeah.

##### **Geohot** [[00:29:38](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1778)]
We'll put it in the bad state, and then we have to reboot the machine.

##### **Nimlgen** [[00:29:43](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1783)]
Yeah, I mean, after like several retries, it will fail. I mean, we just kind of, I know it's just not constantly reproducible, but in some times, yeah, it won't return. Yeah.

##### **Geohot** [[00:29:58](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1798)]
I would try to write like a fuzzer for this. Just something that like, yeah, like put in bad state, even if you have to like spam load fake GSPs eight times. And then, because,

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1813)]
yeah, I mean, there's got to be some way to recover from..

##### **Nimlgen** [[00:30:21](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1821)]
I mean, even the driver, I mean, if it's like, sees the bad state of the GPU, just, you know, it's not going to recover. Yeah. And so, yeah, I would try to write like a fuzzer, just to make sure that it doesn't I mean, the driver, it says, please just do something with the GPU. So, it doesn't do anything to reset the GPU at all.

##### **Geohot** [[00:30:38](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1838)]
Interesting. So, if you insert their driver after it's in this bad state, their driver does not recover. Yeah.

##### **Geohot** [[00:30:47](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1847)]
Yeah.

##### **Geohot** [[00:30:50](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1850)]
I mean, okay. In the worst case, we just have to reboot the machine. Just have to.. We can, we can automate that. Yeah, no, actually..

##### **Nimlgen** [[00:30:57](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1857)]
But, not.. That's the problem happens only if like the.. I mean, we just gracefully shut down the GPU in all cases. But, I mean, what I fixed today is I think some driver tries to probe the GPU while it was like some AST driver. So, just ask DRM to probe the GPU. And I think that was the collision because we also were using the GPU. So, I just disabled it. I think we disabled the AST driver. So, maybe it's gone now.

##### **Geohot** [[00:31:30](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1890)]
Wait, what driver? AST.

##### **Nimlgen** [[00:31:34](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1894)]
AST? AST. AST? AST? AST? AST? AST?

##### **Geohot** [[00:31:43](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1903)]
AST? AST? AST? AST? AST? AST? And then that has a driver. I mean, the AST is a video card. Like that's how like the BMC remote control thing works. But, I'm surprised that it would be probing the NVIDIA. But, yeah, that might make sense.

##### **Geohot** [[00:32:17](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1937)]
Yeah, no, good to disable that. Yeah, I mean, top priority is making this CI stable.

##### **Nimlgen** [[00:32:24](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1944)]
Yeah, I just also tried to repro like deseg file with a GDB memory. attached for three days. I know it just worked fine, but it still happened since then. Got it. Yeah, and the only time I just caught it, it was the Python-related. I still get a lot of running, but yeah.

##### **Geohot** [[00:32:48](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1968)]
Cool.

##### **Geohot** [[00:32:49](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1969)]
How are we doing on the 350x stability stuff?

##### **Nimlgen** [[00:32:54](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=1974)]
I fixed one, like one tuple with the scratch buffers, but still, yeah, I still see weird issues with BIM. Maybe not very often. And actually, it's really strange behavior, and I don't really understand it. Actually, from the driver perspective, 350 is really similar to 300, my 300. Yeah. No, I mean, the strange behavior is that if I just increase the, like multiply the scratch buffer by four, like, MI350 will just silently fail for a kernel. So that's really strange, and I don't understand why. Yeah.

##### **Geohot** [[00:33:41](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2021)]
Is that more scratch buffer than is available on the chat bar?

##### **Nimlgen** [[00:33:48](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2028)]
No, I mean, it's just allocated on the VRAM. So it should be fine. I mean, MI300 works fine with this.

##### **Geohot** [[00:33:57](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2037)]
Wait, scratch buffers in VRAM? Yeah.

##### **Nimlgen** [[00:34:01](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2041)]
I mean, it's, yeah.

##### **Geohot** [[00:34:05](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2045)]
So what's going into the scratch buffer? Is this where it's like storing, like, the registers, or like stores the state for?

##### **Nimlgen** [[00:34:14](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2054)]
I think, yeah, so some stack, maybe, stack-related things.

##### **Hooved** [[00:34:20](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2060)]
Hmm.

##### **Geohot** [[00:34:21](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2061)]
Yeah, I mean, there's a lot of jankiness around this on the RDNA3 cards with, like, the Wave restore stuff that uses that thing. But you know, I mean, we have to figure out, if we're still failing on Beam, we absolutely have to get that fixed.

##### **Nimlgen** [[00:34:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2077)]
Yeah.

##### **Geohot** [[00:34:39](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2079)]
So yeah, that's probably top priority.

##### **Nimlgen** [[00:34:42](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2082)]
I thought maybe Apple would like to just try AM on the MI300. Yeah. But I don't know if, like, more debugging from AM will help to close the problem. But I just double-checked the code, like, in all the calculations we do. I mean, it's correct and matches AMD stuff.

##### **Geohot** [[00:35:06](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2106)]
Yeah.

##### **Geohot** [[00:35:07](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2107)]
I mean, yeah, we can switch to, we don't have AM on MI300X yet, do we? Or either of them? No, we don't.

##### **Geohot** [[00:35:16](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2116)]
How much, what are we missing? I don't know.

##### **Nimlgen** [[00:35:24](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2124)]
I mean, basically, we need maybe some refactors, or just not refactors, just to support JPEG-X9, and the refactor to support XCDs. Cool.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2140)]
Yeah. I mean, whatever is going to fix the stability. I also think that we're going to have to add AQL support.

##### **Hooved** [[00:35:48](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2148)]
Yeah. I mean, I think that's a good thing.

##### **Geohot** [[00:35:51](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2151)]
I mean, I spent a day looking at the firmware, and it looks like the, there definitely is some hot sync path that the GPU is using. There's some sync path that's not doing an atomic in VRAM. But as far as I could tell reading the firmware, there is nothing exposed. Yeah. To PM4 that can do this. The only hope would be, PM4 has a backdoor, which lets you put in AQL commands. But I think we might just want to write AQL support.

##### **Geohot** [[00:36:35](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2195)]
Yeah. I see.

##### **Geohot** [[00:36:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2197)]
Yeah. I mean, we got to get that sync time down, because what, we're still spending like 10 microseconds overhead per kernel?

##### **Nimlgen** [[00:36:44](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2204)]
Yeah.

##### **Geohot** [[00:36:46](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2206)]
Yeah. I think both of them. I mean yeah that stuff all adds up so yeah but yeah I think that's you know we got nine weeks let's make sure by the time we're we got seven before we gotta launch our training run but let's make sure we got this all super stable and up to you whether you want up to you where the priority for getting AM working is if the AMD driver is not causing problems I'm okay with using it but yeah we definitely gotta fix these beam stability issues and get rid of that 10 microseconds of sync

##### **Nimlgen** [[00:37:24](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2244)]
so yeah also did some HTQ refactors and finally we can put CPU compute and like HTQ device compute in the same graph so also CPU is threaded now but it's actually one thread for now that was required for this refactor so but yeah I think we can scale this

##### **Geohot** [[00:37:50](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2270)]
oh so the CPU the CPU compute is no longer running in the same thread as the Python process

##### **Nimlgen** [[00:37:55](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2275)]
yeah

##### **Geohot** [[00:37:56](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2276)]
so one of the things that I'm interested about for that is when I control C it can it actually kill it

##### **Nimlgen** [[00:38:06](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2286)]
yeah I mean it's like a demon demon thread yeah no because I mean that's always been

##### **Geohot** [[00:38:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2293)]
an annoyance whenever you've been using the CPU backend where you control C it if it's in the playroom of course you put a color function it'll take all the cogs or Gprong

##### **Geohot** [[00:38:30](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2310)]
in and will get delayed or a to do but yeah you'd really have to guess

##### **Geohot** [[00:38:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2317)]
how's another bogey inside hide it there we go

##### **Hooved** [[00:38:46](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2326)]
that's

##### **Nimlgen** [[00:38:47](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2327)]
Yeah. So yeah, also try to profile the chain use, which you can use LAMA CPU offloading. But actually, I mean, this is not usable with such amount of data, at least for now. I don't see any kernels, but they are collected. I don't know what's the reason for that.

##### **Geohot** [[00:39:12](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2352)]
What is this?

##### **Nimlgen** [[00:39:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2353)]
Yeah. I mean, I just tried to profile some BERT runs or LAMA runs with WIS. And I actually don't see any kernels at all. But they are collected, and they are not displayed. Actually, there may be something wrong with the timeline.

##### **Geohot** [[00:39:31](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2371)]
Oh, OK. So you found some viz bug. Yeah. Yeah.

##### **Nimlgen** [[00:39:34](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2374)]
Yeah. I mean, it's really hard to use with such amount of data. At least we need to optimize it, because it's just like 8. 8 steps of BERT, and it's not usable on my Mac. Really?

##### **Geohot** [[00:39:48](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2388)]
OK. Klauselin, any thoughts on?

##### **Qazalin** [[00:39:55](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2395)]
It's strange that it doesn't show anything. That's definitely a bug. I'll look at that. For speed, I'll also try to reproduce that.

##### **Geohot** [[00:40:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2408)]
OK.

##### **Chenyu** [[00:40:09](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2409)]
Just post what you were trying to do. Yeah. Just post what you were trying to do. Yeah. And we can start from there. Because everyone's machine has slightly different spec. Sometimes it will try. Sometimes it won't.

##### **Geohot** [[00:40:22](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2422)]
I mean, I've had mostly pretty good luck. It definitely shouldn't scale. It's not like anything in viz should scale with the size of the buffers, right? The number of kernel launches, sure.

##### **Geohot** [[00:40:32](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2432)]
But.

##### **Chenyu** [[00:40:38](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2438)]
Let's start by having everyone trying the same command in the viz channel. Yeah. And decide what should and what is probably.

##### **Geohot** [[00:40:46](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2446)]
That seems like a good way to do this. OK.

##### **Geohot** [[00:40:50](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2450)]
Anything else? No.

##### **Hooved** [[00:40:55](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2455)]
Cool.

##### **Geohot** [[00:40:59](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2459)]
Also, feel free to reach out to the person on Twitter

##### **Chenyu** [[00:41:01](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2461)]
doing the Mac Thunderbolt thing.

##### **Geohot** [[00:41:05](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2465)]
He's either going to get it or not. I don't think there's that much for me to do.

##### **Chenyu** [[00:41:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2468)]
No, no. He's like, hell, I can ask them to open up. And the PR will show up.

##### **Geohot** [[00:41:15](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2475)]
Yeah, yeah. But I think they'll either go out or get it or they won't. I mean, it should be pretty easy. You have to write this. I mean, Apple's gotten ridiculous with how much they've locked things down. But you don't need a kext. You can write something called a dext, which is a driver extension. You still need a weird entitlement. But you don't need to disable system integrity. Yeah. So yeah. And then there's ways to map. I don't know. My talks to ChaiGBT about it, there is not really a way to mmap the bars. But IOCATE gives you a bunch of functions that let you do config reg writes and DMAs. So I think that'd be pretty easy to plug into our stuff. So that bounty is well within doable by somebody.

##### **Nimlgen** [[00:42:06](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2526)]
And then we can write. Yeah. Yeah. Somehow get system memory on the Mac to do B2B.

##### **Geohot** [[00:42:15](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2535)]
Yeah. Yeah. Some way to access whatever the Mac's version of pinned memory is. I don't know how well abstracted that stuff is. But I don't know. We shouldn't be putting time to this. Someone else can figure this out. It would definitely be cool to run 15 IDs from Macs.

##### **Chenyu** [[00:42:32](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2552)]
Cloud. PostParrot's not here. UVM is not here. So we can wait until they are here.

##### **Geohot** [[00:42:40](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2560)]
Let's try something else that works mentally. Rginetty pins OK.

##### **Chenyu** [[00:42:50](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2570)]
Rginelamo. So it should be fine by Performing R Traffic Nous, if we have a remote program. I'll watch it next. Kim Ly. getting close. Yeah so we have one that fix the stream enum stuff and we have one that merges the onX parse and onX into one file then finally the one that merges that single file into TinyGrid proper. So some small like MyPy issue, linting issue and making sure OpenPylet is all supported. So OpenPylet they are trying like a new model which call into the instructions that we didn't implement before so we also want to get that first. Cool. Yeah I think good progress I have been commenting on the PRs hopefully those make sense and just let me know if there's anything that's like way down me and I think it should be good. Yeah Kanban people definitely are excited they are pretty happy with our support of TinyGrid so yeah Kanban people definitely are excited they are pretty happy with our support of TinyGrid so far and they are also using the latest version so everything is like back to good track.

##### **Chenyu** [[00:44:05](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2645)]
Cool. So other bounties we have B1TG and Hoov here you want to say something about your work maybe we start with B1TG. Yeah the reduced access one I see it's

##### **Geohot** [[00:44:17](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2657)]
Draft but I don't know why. Is this closer?

##### **Geohot** [[00:44:24](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2664)]
Not the Draft PR. So he has two PR. Yeah. Oh there's another one. I still use the old PR.

##### **Geohot** [[00:44:36](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2676)]
So you use the old PR okay.

##### **B1tg** [[00:44:39](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2679)]
Let me find that. The new lower last week broke my code I temporarily hack around it. Got it. And maybe fix it properly.

##### **Geohot** [[00:44:56](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2696)]
Shape 1. I don't know how I feel about shape 1. I'm not sure what that's trying to do here. But um yeah I mean I think you're close with this. I don't think process replay needs to match perfectly.

##### **B1tg** [[00:45:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2713)]
Oh I got a problem in the process replay. The second stage is much the get program and the generated kernel can't pass. It must verify.

##### **Geohot** [[00:45:30](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2730)]
Yeah that's totally fine. I don't know. I don't think it really has to match process replay. Um I'm fine with it. As long as as long as it as long as like I saw one of your changes had something where it changed the number of uh Image reads allowed and yeah we can't have that. But if it doesn't match process replay that's fine.

##### **B1tg** [[00:45:52](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2752)]
Okay um I find it hard to get those things passed. Yeah. Okay.

##### **Chenyu** [[00:45:57](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2757)]
I mean it depends on what kind of div right. If you're a div somehow accidentally or I don't know and intentionally change a lot of kernels then it's bad. But if you're saying okay it's just like a few ones that disappear so that it looks slightly different but that's only very local that's fine.

##### **Geohot** [[00:46:15](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2775)]
Yeah or if it's just annoying to get the thing on master to parse the thing I don't I'm not worried about that either. Uh yeah I'm just worried about things that are actual like functionality changes.

##### **Geohot** [[00:46:25](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2785)]
But otherwise um yeah let me know when it's ready and we'll merge it.

##### **B1tg** [[00:46:41](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2801)]
So Chenyu you said before the generated kernel should stay the same. You mean the AST or the source code? No the source. Kernel source. The source code.

##### **Chenyu** [[00:46:53](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2813)]
Because definitely your AST would change. Uh not definitely but very likely that would change because now there are semantics of those reduced axes. So the argument or I don't know the output of that would be different. But since what in shape is never real it shouldn't change the output kernel source.

##### **B1tg** [[00:47:17](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2837)]
Oh the for the meta is the C code. You mean the kernel source. Yes.

##### **Geohot** [[00:47:26](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2846)]
Yeah right like in theory the C code shouldn't change but I'm not super hung up on it being identical. Like only if there is. But how can that be different? Oh the names literally the names.

##### **Chenyu** [[00:47:39](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2859)]
Oh sure so so I mean if the difference is like RIDX indexing nulls instead of starting from zero it starts from one. That to me is the same.

##### **B1tg** [[00:47:48](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2868)]
Oh okay.

##### **Geohot** [[00:47:49](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2869)]
Yeah yeah like it doesn't have to be byte for byte identical but.

##### **Chenyu** [[00:47:52](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2872)]
But if your kernel suddenly have one more for loop. Yeah that's that's bad.

##### **Geohot** [[00:47:57](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2877)]
Yes it shouldn't have it shouldn't change the loop structures.

##### **Chenyu** [[00:48:01](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2881)]
Yeah that's what I mean.

##### **Geohot** [[00:48:02](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2882)]
Yeah. Okay.

##### **Geohot** [[00:48:06](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2886)]
Yeah they don't need to be byte for byte identical.

##### **Chenyu** [[00:48:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2888)]
Yeah the under the hood the compute should be the same. The symbol name can be slightly different that's fine.

##### **Geohot** [[00:48:14](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2894)]
Yeah. Even I mean yeah it should. Again I'm I'm even gonna be less picky than this. I mean I'd like to get this merged. Uh. As long as as long as there's no like regressions and speed of anything then.

##### **Chenyu** [[00:48:29](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2909)]
Yeah yeah we're good. And I mean it doesn't also need to be a one PR if you like and you have like smaller changes like maybe just change things locally. We can also merge that separately.

##### **B1tg** [[00:48:43](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2923)]
Okay I I don't don't think it's a ready now. Okay. The lower stuff thing seems very bad.

##### **Chenyu** [[00:48:53](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2933)]
Uh yeah so don't write hacks. Uh try to understand in what stages one are capped and see if you can like remove it gradually or just remove it at one go. That's fine but don't write more stuff just just to this is supposed to be making stuff simpler so not adding more functions and states to to to to work on this.

##### **B1tg** [[00:49:18](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2958)]
Okay. That's because the. The X. Uh the uh. Because these don't keep them anymore. So the. Uh I can't get the access. Oh so. In the callback.

##### **Chenyu** [[00:49:40](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=2980)]
Uh I don't know unless you I would need to see a more specific example to like you can describe like what you want and what it's not happening then I can maybe take a look. But anyway you know. You know. You know the drill you know the principles. Uh we want the. Under the hood behavior to stay the same and we want the intermediate representation to change to. Uh to change that behavior. So. Whichever way to find. Easy and again similarly. I don't know what's the best way to deal with this because for the moving upcast one I probably have like 10 prs that each change things slowly that I can understand. So I don't know if this is easier for you. Just let me know. I can review this whenever.

##### **Geohot** [[00:50:29](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3029)]
Okay. Cool. Uh we have training stable diffusion.

##### **Chenyu** [[00:50:40](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3040)]
So I don't. Really know how long it's expected to take if you can give me uh also it looks like your link doesn't give permission.

##### **Chenyu** [[00:50:50](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3050)]
Your weight and bias link. Yeah.

##### **Hooved** [[00:50:52](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3052)]
I need to fix that. Yeah. I'll fix that after the meeting. But. Uh yeah. I mean that one to two day. It's like roughly 32 hour estimate assuming that um like if I you know the the reference smallest batch size is 512 I think. And uh that converges after like 3 million examples.

##### **Geohot** [[00:51:14](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3074)]
Uh okay.

##### **Hooved** [[00:51:16](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3076)]
And so it'll take me 32 hours to process 3 million examples. With my current training loop. Um I think it could be a lot faster just based on I'm only getting 70 teraflops. Um you know.

##### **Geohot** [[00:51:32](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3092)]
Uh let's see.

##### **Chenyu** [[00:51:37](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3097)]
So I'd like to see how you expect the full run to take. It can be you can extrapolate this from our previous submission um on BERT and comparing to other people's submission and their submission. Okay. And then I'd like to see that estimation. Then.

##### **Hooved** [[00:51:57](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3117)]
I don't quite understand what you mean. So I'm comparing to the MLPerf reference like their number of examples.

##### **Chenyu** [[00:52:04](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3124)]
Yeah. I mean I mean I I'd like to know how long you expect the training run to take.

##### **Hooved** [[00:52:10](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3130)]
Yeah. I'm I'm saying if I ran the training run on the full data which I could do today if I wanted. I would expect it to take 32 hours.

##### **Chenyu** [[00:52:19](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3139)]
And how long.

##### **Hooved** [[00:52:20](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3140)]
If it converged. If it converged in the same number of examples.

##### **Chenyu** [[00:52:26](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3146)]
Uh cool that's fine. 32 hours.

##### **Geohot** [[00:52:28](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3148)]
Yeah run it. See if it converges.

##### **Hooved** [[00:52:32](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3152)]
Okay.

##### **Chenyu** [[00:52:33](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3153)]
So I mean I mean if if you give me an instruction I can run this on MI300x and that should finish a lot faster. That also work.

##### **Hooved** [[00:52:44](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3164)]
Uh so. I mean like I don't want to just try it and babysit it since it you know. Um. I mean if you are.

##### **Geohot** [[00:52:51](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3171)]
You want to just give Maxis to MI300x?

##### **Geohot** [[00:52:54](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3174)]
Okay. Uh let's see.

##### **Chenyu** [[00:52:59](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3179)]
Oh let's try this. Yeah let's let's start with the 32 hour. Yeah 32 hour on a red sounds good. Yeah 32 hours on red and it will be good if you can also have some like logins. The WMB link then if it if it all looks good then sure bounty is yours. Then we would I'd like also to try that on MI300x. Yeah.

##### **Hooved** [[00:53:23](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3203)]
Okay um the data sets like 800 gigabytes there's enough room on the RAID array on tiny R5 can I but it's like most of the free space can I just download it?

##### **Geohot** [[00:53:35](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3215)]
Oh. Like the full training. Yeah that's fine. Yeah. Yeah.

##### **Chenyu** [[00:53:40](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3220)]
We don't have enough drive now. That's not there. R5? We should have. No but we have a lot of like there's like one terabyte for work. Oh yeah you're right. Yeah you can use yeah.

##### **Geohot** [[00:53:50](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3230)]
No no don't delete. No don't delete anything but yeah you got you got 1.3 terabytes free you can use it. Sure.

##### **Hooved** [[00:53:56](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3236)]
So my my only other concern is that it won't converge because I haven't tuned the learning rate for my much smaller batch size. Um so my my question I I just wanted to know if I could do gradient accumulation even though it's not anywhere in the reference.

##### **Chenyu** [[00:54:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3253)]
So you can do gradient I don't know I don't think that changes anything.

##### **Chenyu** [[00:54:20](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3260)]
Uh no because now you can train with effectively much bigger batch size. So I I'm pretty sure the reference they all use a lot.

##### **Geohot** [[00:54:29](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3269)]
I say I mean the the rules for the boundary or whatever is legal under MLPerf rules so.

##### **Hooved** [[00:54:35](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3275)]
Well that's what I'm asking is it legal to do gradient accumulation even if it's not explicitly anywhere in the reference like the reference doesn't have to be.

##### **Chenyu** [[00:54:43](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3283)]
So I don't know about that but again if you have a wrong lag trends by your estimation. 32 hours and it's just off by a little bit I can run this or we can grant you access to a much stronger machine and you can turn your learning rate layer. But I I I can only comment after I have seen something being trained now it's a lot it's hard to say.

##### **Hooved** [[00:55:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3308)]
Okay that's fair enough.

##### **Geohot** [[00:55:09](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3309)]
I mean it'd be hard for me to believe that gradient accumulation violates MLPerf rules somehow it depends on the benchmark.

##### **Hooved** [[00:55:18](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3318)]
What I've noticed. From reading the rules like some of the benchmarks explicitly have gradient accumulation steps as a hyper parameter it's always unrestricted when it is listed. Yeah. But it's not listed.

##### **Chenyu** [[00:55:32](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3332)]
Because in principle what they are saying is if it's equivalent in math and it's fine so I would think yes but again I don't think this bounty if you're trying something 32 hours and it's just off by. Reason amount of amount. That's tunable by hyper parameter land grant you a bigger machine or whatever then we tune that.

##### **Geohot** [[00:55:56](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3356)]
I mean definitely to claim the bounty I want one that hits the MLPerf target.

##### **Chenyu** [[00:55:59](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3359)]
Yeah of course. But yeah I'm not that worried about. Yeah just just like so. So I guess back to practical thing. Yeah you can just start with your wrong and if you're confident enough we can grant you a bigger machine though so that's fine. That's fine. All right. Yeah. I just want to see something that's being trend and seems to learn something before greater more resource. That's.

##### **Hooved** [[00:56:26](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3386)]
All right. The current link does show that but on point one percent but yeah. Fair enough. All right. Thank you. Sure. Okay.

##### **Geohot** [[00:56:36](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3396)]
Oh and then the move on optimizer. I'm upset at how many times I'm going back and forth on this right like there's a bunch of little things like that fused. Optum right. So instead of like just fuse optum work or it doesn't work if it doesn't work you shouldn't just set the default to zero you should add an assert saying you can't use this flag with move on. I don't know if move on is actually 2D. The shape of the gradient matters.

##### **Chenyu** [[00:57:05](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3425)]
Yeah that's what was first.

##### **Geohot** [[00:57:07](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3427)]
Yeah it's crazy.

##### **Chenyu** [[00:57:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3428)]
So I will leave this to was perfect. Yeah it's much better than what this should be.

##### **Geohot** [[00:57:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3433)]
Yeah. No just there should be an assert for it. Right. And then like all this back and forth about the like the momentum thing and the hyper parameters thing like it should be like this thing has to be usable fundamentally like I don't want something that has hyper parameters that oh well they match the other ones. Yeah but doesn't work. It's useless. And I'm still seeing so there's a momentum change. I'm still seeing multiple changes here that I don't really understand. Like I don't really understand why you need to check in three places if NS params is none. Like what's different and why why can't that be computed beforehand maybe it can always be computed afterward. The smaller diff to these optimizers the more likely I am to merge this. And I just I see like a bunch of little things in the PR where it's like no the word classic is not under is not under the word self and like it's just little things it's like okay you didn't read this 17 times. So.

##### **Geohot** [[00:58:09](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3489)]
Okay.

##### **Geohot** [[00:58:13](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3493)]
I don't know how many times I've read this. I don't think Cavs is here. But yeah that's my that's my take on Mulan.

##### **Chenyu** [[00:58:20](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3500)]
Yeah. So because these are like higher level stuff and higher level stuff is similar to everything we put in tensor. That's what's the user of tiny group will read. We don't expect a user to read like lower or much lower level stuff. But for anything and again in optin in rate schedule learning risk scheduler or tensor user will read. So we want to make sure. These are really clean and readable to even like external users.

##### **Geohot** [[00:58:51](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3531)]
Okay. All about the CIFAR.

##### **Geohot** [[00:59:02](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3542)]
Oh yeah. No that's never gonna happen. I shouldn't do that. No. Okay. I should just pay out that bounty. If it's right it's right.

##### **Chenyu** [[00:59:14](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3554)]
I don't know what's the issue with whisper. What's the whisper bounty.

##### **Geohot** [[00:59:19](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3559)]
It's not ready. I always hear updates. They're long updates and they're not ready. It's not ready yet.

##### **Chenyu** [[00:59:23](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3563)]
No but this update something is saying something else. Right. I saw the bounty is just making whisper running in web GPU. Yeah. He's talking about the model quality and different heuristics.

##### **Geohot** [[00:59:36](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3576)]
Yeah. I don't think that that's required for the bounty. I think all that's required for the bounty is that. It runs in web GPU and it matches whatever the opening eye reference is. Like whatever opening eye reference is if you show that it's the same quality as that. That sounds fine to me. Yeah.

##### **Geohot** [[00:59:53](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3593)]
Okay. Yeah. I think that's it.

##### **Hooved** [[01:00:03](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3603)]
Cool.

##### **Chenyu** [[01:00:05](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3605)]
Looks nice. Thank you everyone. See you next week.

##### **Geohot** [[01:00:08](https://www.youtube.com/watch?v=jH9ra0-bRiw&t=3608)]
Bye. Bye.
