# 2025-06-30 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- scheduler kernel ops stuff
- tests with uop and kernel dataset
- mlperf llama 405b
- viz tooling
- drivers
- cloud, tinyfs
- z3 symbolic
- onnx
- local
- other bounties (retinanet, cloud sync stuff, refactors, SVD, cifar torch backend)


### Audio

[Youtube Link](https://www.youtube.com/watch?v=U-UYchhy_dY)

### Highlights

- **[Company Update](#geohot-000000)**: Tinybox v2s are shipping and will be caught up this week, the AMD contract is signed, and the company successfully debunked the AI startup "etched".
- **[Scheduler Kernel Ops Stuff](#geohot-000409)**: After studying Halide, Geohot plans to simplify the optimization space by removing concepts like `keep_dims` and `full_shape`, and fixing fusion by generating new ranges for each reduce.
- **[Tests with UOP and Kernel Dataset](#chenyu-001246)**: The team agreed to delete brittle tests with hardcoded UOPs and plans to put the generation of the kernel dataset into CI for easier access.
- **[MLPerf Llama 405b](#chenyu-001416)**: The 8B model is hitting a memory bottleneck with a long context length; the next steps are to improve memory visualization and implement sharding to get it working on multiple GPUs.
- **[Viz Tooling](#qazalin-002123)**: A memory graph tool has been merged to visualize memory allocation, which will be enhanced to trace buffers back to the kernel graph to help debug high memory usage.
- **[Drivers](#nimlgen-002646)**: The driver for the NVIDIA 4090 is merged and working, with ongoing work to improve performance by implementing huge pages; future work will focus on optimizing performance for the MI300X.
- **[Cloud, tinyfs](#wozeparrot-003453)**: The goal for the week is to get tinyfs operational and decommission the old provisioning machines.
- **[Z3 Symbolic](#siedlykles-003727)**: Work is progressing on the view/const refactor, and the fuzzer for individual rewrite rules has been switched to a more thorough (but slower) bit-vector based approach.
- **[ONNX](#chenyu-004736)**: A refactor to correctly handle float16 types is merged; a known issue causing slow model loading needs to be addressed, likely by moving the loading process to Python.
- **[Local](#ignaciosica-005005)**: A PR to fix aggressive gating on local group stores has been opened, and a refactor of the yellow backend has begun to simplify the code.
- **[Other Bounties](#chenyu-005603)**: Progress is being made on RetinaNet, SVD, and the CIFAR Torch backend bounties, with PRs open for review.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=0)]
I'm going to start with some company update. Tinybox v2s are shipping. I think we're going to be all caught up this week, which means if you order them, they are going to ship out right away. That's good. AMD contract signed. Work started on that. That's pretty much it. We did very well on our beef with etched this weekend. The latest in fake AI startups. I've been getting DMs from people about the etched thing. It's way worse than you think it is. They've never taped out a chip. I guess this isn't related to us, but I can't believe the more you work on this.

##### **Chenyu** [[00:00:49](https://www.youtube.com/watch?v=U-UYchhy_dY&t=49)]
For the audience in this meeting, that's not aware of it. You have, I give you three minutes to go through this.

##### **Geohot** [[00:00:56](https://www.youtube.com/watch?v=U-UYchhy_dY&t=56)]
Yeah, so etched is this company that's claiming they're going to tape out some chip that is a transformer ASIC, which gets 20x performance over H100s. But this is nonsense. 70% of time and power spent on transformers is just spent in gem. GPUs are already pretty close to ideal gem machines. I did learn something really interesting. So apparently their plan was a 2048 by 2048 systolic array. Just make a huge systolic array and then you can calculate one transformer, but this doesn't work. Chatchypt did this whole analysis on it and says basically the ideal size for a systolic array is 128 by 128 because you have losses in the wires. You don't want to make wires really, really, really long, right? And think about why. If you make a really, really long wire, that wire is going to have capacitance. And then you have to use more power to drive that wire. So yeah, the whole plan is utterly nonsense. I'm happy we debunked them with Twitter. So that's that's that situation. And GPUs are really like really close to optimal. So another point in us not making our own chip anytime soon.

##### **Geohot** [[00:02:24](https://www.youtube.com/watch?v=U-UYchhy_dY&t=144)]
But yeah, no, it's very.

##### **Geohot** [[00:02:27](https://www.youtube.com/watch?v=U-UYchhy_dY&t=147)]
AMD is very exciting. Like I think I think that AMD is really going to be brought on par with Nvidia in like a couple of years and then. Yeah, we're in like a much more of a commodity landscape.

##### **Chenyu** [[00:02:40](https://www.youtube.com/watch?v=U-UYchhy_dY&t=160)]
Oh, have we received a new machine?

##### **Geohot** [[00:02:42](https://www.youtube.com/watch?v=U-UYchhy_dY&t=162)]
We've not received a new machine and we haven't gotten paid yet. But I don't know. These things just take a long time. Technically, they have like three months to pay us or whatever. It's not the one need the money. And the new machine, but it's not that different from the old machine. I'm pretty sure the work size is still 64 on CDNA 4. Yeah, okay, then nothing really changed.

##### **Geohot** [[00:03:06](https://www.youtube.com/watch?v=U-UYchhy_dY&t=186)]
Uh-huh.

##### **Geohot** [[00:03:09](https://www.youtube.com/watch?v=U-UYchhy_dY&t=189)]
Okay.

##### **Chenyu** [[00:03:13](https://www.youtube.com/watch?v=U-UYchhy_dY&t=193)]
We so do you have any box red V2?

##### **Geohot** [[00:03:19](https://www.youtube.com/watch?v=U-UYchhy_dY&t=199)]
Whoa, red V2. I haven't heard anything about that. We have we have tiny box red. We have to sell tiny box red.

##### **Geohot** [[00:03:27](https://www.youtube.com/watch?v=U-UYchhy_dY&t=207)]
We have two more tiny.

##### **Geohot** [[00:03:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=211)]
We have to sell the tiny box red first. I'm not going to make V2 if we haven't sold all the reds. I have two of them just sitting there still. Okay. The government bought two of them after a long ordeal. Uh, we're so too. Yeah, maybe another 17 business months. Yeah.

##### **Chenyu** [[00:03:56](https://www.youtube.com/watch?v=U-UYchhy_dY&t=236)]
Great. Okay. That was good. Okay. I don't know what you'll call your stuff, but your stuff is next.

##### **Geohot** [[00:04:09](https://www.youtube.com/watch?v=U-UYchhy_dY&t=249)]
Yeah. So I did a lot of reading last week on so highlight is like the good one of these.

##### **Geohot** [[00:04:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=256)]
Uh, MLIR seems to be this like ecosystem of big team.

##### **Geohot** [[00:04:29](https://www.youtube.com/watch?v=U-UYchhy_dY&t=269)]
500 line things to express one rewrite rule kind of kind of stuff. Uh, then TVM started with halide, but the main problem I've seen with TVM is they've just added everything to it. Like TVM can interface with everything and you know when you when you try to do everything you get nothing. Um, but halide is the OG good one and they've basically broken down all types of optimizations into. Uh, pretty much four types. Uh, two and a half of which we have. Um, there's one that we don't really talk about. And the one that we don't talk about is like when you want to do recomputation. So halide has a good language for that and we can kind of move to it, but where what I realized reading all this stuff is that. We've massively overcomplicated. Like what's really a very simple optimization space now and I'm just working through all the refactors required to expose that simplicity. Um, also fixing the lower fixes all of these fusion things like you want to use every time there's a reduce that reduce basically creates ranges. You don't want to try to reuse ranges that already exists somewhere and then you can think about doing range fusion later on. Um, it's a lot easier to do to do fusion than it is to do splitting. Because if you think about it like if you want to split something into two, you have to look at children. If you want to take things that are already two and just make them one will just replace all instances one to be the other. That's an easy that's like an easy operation. So yeah, well, we'll generate the reduces with all the ranges every reduced that's created gets a new range and then we can think about range fusion later. And then we can specify on roles on each one of those ranges completely separately. And this just like fixes all of that weird stuff about multi reduces. Yeah, but the thing that I really want to get in that's still going to require a bunch of refactors is removing keep dims from the reduces. Uh, the reduce should remove the reduced dimensions. It should not leave ones dimensions with ones are total nonsense and should be removed from everything. They do nothing.

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=420)]
Uh, you don't need stop. Working toward that.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=U-UYchhy_dY&t=427)]
It's going to take.

##### **Chenyu** [[00:07:09](https://www.youtube.com/watch?v=U-UYchhy_dY&t=429)]
I was also plan for all the full shape and all those permute and reshape in kernel.

##### **Geohot** [[00:07:18](https://www.youtube.com/watch?v=U-UYchhy_dY&t=438)]
So full shape is also nonsense. You can have full shape because if you have a parallel multi reduce over different size dimensions. Like that thing that causes the trouble with the thing that makes the a range fuser way too complicated. Um, there's no such thing as a full shape. You you can have things with.

##### **Chenyu** [[00:07:37](https://www.youtube.com/watch?v=U-UYchhy_dY&t=457)]
Yeah, but there's code in front of us and there's some other logic that requires let's know.

##### **Geohot** [[00:07:45](https://www.youtube.com/watch?v=U-UYchhy_dY&t=465)]
Well, yeah. I mean, okay, so I took a big thing out of the lower already the GPU dimensions have been refactored out of the lower. Uh, but the thing that I haven't refactored out of kernel yet is the tensor course. And that's the until we do that, it's really hard to delete kernel. So that involves upcasted warps, but I don't know. I'm just going to leave all this. I think we can get flash attention without any of this and I think we can get fast jam without any of this. So like to keep this project scoped in something that's concrete. My goal is at the end of like a month or two to have a really fast jam and a really fast flash attention on the M300.

##### **Geohot** [[00:08:33](https://www.youtube.com/watch?v=U-UYchhy_dY&t=513)]
I don't yeah, I think we can leave the full set of shapes off.

##### **Geohot** [[00:08:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=516)]
I think it's not that not that bad.

##### **Chenyu** [[00:08:40](https://www.youtube.com/watch?v=U-UYchhy_dY&t=520)]
Just hard to replace with something else.

##### **Geohot** [[00:08:43](https://www.youtube.com/watch?v=U-UYchhy_dY&t=523)]
Well, yeah, and we can also just like not optimize in that case. You don't actually need kernel.py. You if cur if kernel.py detects this weird case, you can just say don't use it.

##### **Chenyu** [[00:08:55](https://www.youtube.com/watch?v=U-UYchhy_dY&t=535)]
No, what happened to highlight is similar to pretty active still.

##### **Chenyu** [[00:08:59](https://www.youtube.com/watch?v=U-UYchhy_dY&t=539)]
Do people use it now?

##### **Geohot** [[00:09:02](https://www.youtube.com/watch?v=U-UYchhy_dY&t=542)]
So I had lots of conversations with chat to be T about this. ML stuff is not using halive and there is a few problems mostly with its implementation. Such that an ecosystem didn't sort of form around it. So like for example, halide only supports five dimensions. It's like it's not a real limitation. It just happens to be the way the things are written. The thing is written so much with like this idea of image processing. The buffer is even called image. People just didn't like that. So a lot of the ML stuff moved to places where there were these ecosystems. Like MLIR is an ecosystem and TV Amazon ecosystem. And yeah, so that's why people don't know.

##### **Chenyu** [[00:09:50](https://www.youtube.com/watch?v=U-UYchhy_dY&t=590)]
Because on their read me good up page it also says it's supposed like kuda open sale, metal, welcome. Basically the things that we support or we're on the support.

##### **Geohot** [[00:10:03](https://www.youtube.com/watch?v=U-UYchhy_dY&t=603)]
So it does it supports metal. I got it out putting metal stuff. You can definitely output all this stuff. GPUs were a bit more of an afterthought. They added on like a bunch of kind of hacky things to the optimization language. It's clear that it's all designed for CPUs. It's also missing a like a good. It doesn't have anything like our memory scheduler. So it's not that good with like these this idea of multi kernel memory scheduling. That's something that like TVM has and that we have. And actually they don't really support Qualcomm. Their Qualcomm support is all out of tree. Same as ours. Because because of the complexity of Qualcomm. Like the haylight PhD is really, really good. Like it's super readable and it explains clearly this like it has this like triangle that says basically you have a choice between. I'll get the I'll get the triangle. I posted it in the theory channel.

##### **Geohot** [[00:11:20](https://www.youtube.com/watch?v=U-UYchhy_dY&t=680)]
Parallelism, locality and redundant work. And you have to do you have to do tradeoffs in it.

##### **Geohot** [[00:11:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=691)]
So like it's easy if you don't care about doing lots and lots of redundant work. Okay, it's trivial to trivial the trivial to make everything parallel and local. But then you're like well, but I don't want to do all that redundant work. Okay, but now what you're going to do save that. Okay, that limits locality. If you're okay with no parallelism, sure you can get perfect locality with no redundant work.

##### **Geohot** [[00:11:54](https://www.youtube.com/watch?v=U-UYchhy_dY&t=714)]
I'm just you know, do everything. Locally. Is this person not? Oh, the haylight person. He works at Adobe.

##### **Chenyu** [[00:12:18](https://www.youtube.com/watch?v=U-UYchhy_dY&t=738)]
Oh, that's why Adobe and Google are the only two big companies that you said.

##### **Geohot** [[00:12:25](https://www.youtube.com/watch?v=U-UYchhy_dY&t=745)]
Yeah, I mean, yeah, he was at Google and then he moved to Adobe. A lot of the a lot of the Photoshop tools are written in haylide.

##### **Geohot** [[00:12:35](https://www.youtube.com/watch?v=U-UYchhy_dY&t=755)]
Okay.

##### **Geohot** [[00:12:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=756)]
Okay.

##### **Geohot** [[00:12:39](https://www.youtube.com/watch?v=U-UYchhy_dY&t=759)]
Yeah.

##### **Geohot** [[00:12:41](https://www.youtube.com/watch?v=U-UYchhy_dY&t=761)]
Sounds good.

##### **Chenyu** [[00:12:44](https://www.youtube.com/watch?v=U-UYchhy_dY&t=764)]
Okay, let's move on.

##### **Chenyu** [[00:12:46](https://www.youtube.com/watch?v=U-UYchhy_dY&t=766)]
I want to quickly think so we delete. We delete some tests that was returned with like a very hard code you up style. That's very hard to update. Now we are refactoring again and changing lots of stuff. There are still more. Do we want to just remove them or remove? Funnily picked the blocks stuff.

##### **Geohot** [[00:13:10](https://www.youtube.com/watch?v=U-UYchhy_dY&t=790)]
I'm mostly I'm mostly okay with deleting it. I don't think we really have to do it proactively. I think but once there is. Once these tests are failing, I think it's better to just delete them. And we shouldn't be writing tests that like hard code huge you up strings that are copying pasted.

##### **Chenyu** [[00:13:29](https://www.youtube.com/watch?v=U-UYchhy_dY&t=809)]
Chrono did also does another thing. I remove like 90% of the stuff in that script. It runs like under two minutes on my machine. So hopefully that's a lot better now. I don't really want to change that but some scripts relying on the data set networks. So find this.

##### **Geohot** [[00:13:50](https://www.youtube.com/watch?v=U-UYchhy_dY&t=830)]
I think we should put the generation of it in CI and you can just download it from CI. Yeah, it's probably better. I don't know. Auto update or anything but yeah just another worker that does that.

##### **Chenyu** [[00:14:06](https://www.youtube.com/watch?v=U-UYchhy_dY&t=846)]
Okay, I can do that. Cool.

##### **Chenyu** [[00:14:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=856)]
I think we're creating loop for a b is pretty much there. The only bottleneck. The main bottleneck now is. This was a context lens of a one night to cause all the memory. And I don't know when we compute comment was the V-Round we need. Do we include anything that we need to save for the back or from. Running with the sequence. Like the activation or any intermediate thing that requires the story for the back.

##### **Geohot** [[00:14:58](https://www.youtube.com/watch?v=U-UYchhy_dY&t=898)]
We have.

##### **Chenyu** [[00:15:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=900)]
I don't know. Yeah, because we are certainly stuff that we compute in the forward as a function of your input lens.

##### **Geohot** [[00:15:13](https://www.youtube.com/watch?v=U-UYchhy_dY&t=913)]
That's why like impolence with 3000 works by 8000 doesn't work. Yeah, we got to just make the tooling for this better so we can see it easily. Yeah, and I will so.

##### **Chenyu** [[00:15:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=931)]
I wanted to either understand that I sure or I will start I was starting to I started to add like charting. Since a b works in one GPU I will expect like 70b to work with 8 GPU. And I was testing like charting 8 on two and. I think that's an. Beth thing happened so I probably need to read this FSTP or is it like different kinds of parallelism.

##### **Geohot** [[00:15:59](https://www.youtube.com/watch?v=U-UYchhy_dY&t=959)]
So before we think about charting. Does it work with fuse opt-in.

##### **Chenyu** [[00:16:10](https://www.youtube.com/watch?v=U-UYchhy_dY&t=970)]
Okay, used a lot more memory.

##### **Geohot** [[00:16:12](https://www.youtube.com/watch?v=U-UYchhy_dY&t=972)]
Yeah, okay, we have to fix that first.

##### **Chenyu** [[00:16:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=976)]
So what FSDP is is like you can do because eventually we will put the optimization stuff around CPU. Well, yeah, we have to do fuse opt-in first.

##### **Chenyu** [[00:16:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=996)]
Why is that okay?

##### **Geohot** [[00:16:41](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1001)]
Because you when you're doing that copy.

##### **Geohot** [[00:16:46](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1006)]
You don't want to the optimizer update should really just be one thing. I guess you in theory could do each one on the CPU and like copy each thing. Oh, no, I don't want to. Yeah, I guess it's all on the CPU that maybe it's actually okay.

##### **Chenyu** [[00:17:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1020)]
But that was the main reason I thought about it and I was like, okay, maybe we don't need any of the optimizer charting stuff because it's on.

##### **Geohot** [[00:17:10](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1030)]
Yeah, maybe we don't actually. Yeah, I mean, so this would just be for charting the M and the V. We have to make sure that the gradients are only on the GPU that has the charted that has the weights. Or at least the gradients are sharded in the same way the weights are. I don't know if that works.

##### **Chenyu** [[00:17:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1051)]
Yeah, I think that's the idea, but now there are like. I don't know.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1063)]
I mean, we actually we also choose which kind of sure.

##### **Chenyu** [[00:17:46](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1066)]
I think we need to worry more about the intermediate buffer less required for backward and also the gradients more than the M MV.

##### **Geohot** [[00:17:55](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1075)]
Yeah, that's probably. Yep.

##### **Chenyu** [[00:18:04](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1084)]
So next goal is for me is to make 70 B. Harding works. I think this requires understand memory because I was not easily trying to. And instead of one GPU using 50% of a memory, now I have to 2 GPUs use both using 90% of a memory and I don't know what.

##### **Geohot** [[00:18:27](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1107)]
Yeah, well, I mean, I think I think we all sort of have a. We also have a job to do for for llama 405 Bay. Yeah, I mean, you're on the.

##### **Chenyu** [[00:18:39](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1119)]
I'll tell you the gradually adding features so we can work with bigger and bigger models with more and more pieces that we will need eventually for or why we're training in the script. Can we train 8B according to the like the rules? So a one that who doesn't work. So let's look immediate blocker. It cannot even.

##### **Geohot** [[00:19:02](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1142)]
Can we train a B with 2048 or something?

##### **Chenyu** [[00:19:06](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1146)]
Oh, yeah, I think so.

##### **Geohot** [[00:19:08](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1148)]
Yeah, I think I think we should do that. I think we should just like start getting runs going and then start pushing these things up.

##### **Chenyu** [[00:19:13](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1153)]
I think we'll learn how to pad the impulse. Yeah, one of the only thing for 405 B is there's no reference. There's no real reference implementation. Just throw you like a Nemo link and say insta Nemo and what the wrongs is a reference. Wait, but yeah, but that stuff's got to be open source, right? It's open source, but it's like reading torch. So you want your optimizer. Okay, it's an abstraction layer of stream. Add them W put in silat and go figure who calls it will create this.

##### **Geohot** [[00:19:56](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1196)]
Yeah.

##### **Geohot** [[00:19:59](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1199)]
But I promise you that every single batch is the same. There's nothing with variable lanes at train time of any of these elements.

##### **Chenyu** [[00:20:09](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1209)]
No, so they use variable, but it's not like penches for every example. They use different lens for training for original not for ML proof.

##### **Geohot** [[00:20:19](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1219)]
Yeah, there's no way. There's no way that anyone's doing variable lanes for any modern. Now I'm training.

##### **Wozeparrot** [[00:20:26](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1226)]
Are they doing sequence packing?

##### **Geohot** [[00:20:28](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1228)]
I don't know that is.

##### **Wozeparrot** [[00:20:29](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1229)]
Yeah, if you have like a shorter sequence, you just throw another one on and you change attention mask.

##### **Geohot** [[00:20:34](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1234)]
Yeah, I think that's right. Oh, you say they change the mask so it can't pay attention to the old one. Yes, that seems plausible.

##### **Chenyu** [[00:20:45](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1245)]
Okay, I don't know if you if was per you think you are better at figuring out what is really being used. I can work with you later. I'll take a look. I was struggling with people. Creating torch. It's a same live. Yeah, I'm on the better fight. Anything I put in a script, I have a reference link. I'm pretty sure that's what's being used. I don't think we'll be challenged once we submit the wrong. So first let's.

##### **Chenyu** [[00:21:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1276)]
Great. Okay, what's last set? Let's move on to this.

##### **Qazalin** [[00:21:23](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1283)]
Emerge the memory graph that you can try it out. It's a master. And yeah, I'm going to work on this. A way to go from like a buffer to the actual kernel to the actual node in the kernel graph. They can see clearly like which buffer. It's hold on to and why I tried llama. It looks like the. Graph just grows. And it allocated 24 gigabytes.

##### **Chenyu** [[00:21:58](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1318)]
So you say you tried llama. What was the thing to try?

##### **Qazalin** [[00:22:03](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1323)]
Just a script that you merged with the ML product.

##### **Chenyu** [[00:22:08](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1328)]
Mama training.

##### **Chenyu** [[00:22:10](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1330)]
So by default, it runs with a B model. And that certainly doesn't fit for a single 24 gig.

##### **Qazalin** [[00:22:22](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1342)]
Yeah, it's out of memories.

##### **Chenyu** [[00:22:25](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1345)]
So if you want to try on the regular tiny box, you can change the llama size to 1B. And that will fit. And I believe give you a similar pattern as in terms of training and parameters stuff.

##### **Geohot** [[00:22:39](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1359)]
And if they should also. It should all work with the null back end too, right?

##### **Qazalin** [[00:22:43](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1363)]
Exactly. I was gonna say that it works completely with the null back end. And you see it. I will get 100 gigs. And it goes down eventually, but we need to figure out why it.

##### **Geohot** [[00:22:56](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1376)]
So much.

##### **Qazalin** [[00:23:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1380)]
The everything like they entire pattern is completely clear.

##### **Chenyu** [[00:23:05](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1385)]
Yeah, so I think one one thing will be really interesting. Not necessarily llama, but. So we talk a lot about like the buffers we stores in the four words. So that is needed for backwards. And this tools can show like what's being stored in the four words later used in.

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1405)]
Backward will be useful.

##### **Qazalin** [[00:23:30](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1410)]
See, so do you want to see like the you off or the actual kernel?

##### **Chenyu** [[00:23:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1416)]
I'm not exactly sure, but it's more of so we always worry about our receiving too much stuff like for the activation. We might in some case store post the input to the activation and the output. But you can imagine it's we only need to store input. If we really want to open it, we can recompute. So to make these decisions, we want to first understand what's what's the current behavior and will be useful to know like what buffers are we. Store, even if we already reach the loss and start to do the back.

##### **Geohot** [[00:24:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1456)]
The long edges between your thing before your loss and after your loss.

##### **Qazalin** [[00:24:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1471)]
I'm thinking like maybe we can have the line number location like kind of like metadata.

##### **Chenyu** [[00:24:43](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1483)]
So I think we're trying to find if there's no really a line for backward. Backward is kind of right from the rewrite rules.

##### **Qazalin** [[00:24:54](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1494)]
I think you can backtrack it. I'll see.

##### **Chenyu** [[00:24:57](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1497)]
Yeah, so the use case I have in mind is I'm training a model and for example, I know the model is say two gigs and I know the gradient of that is another two gigs. But now I'm seeing a max RAM I was using was eight gig, so which means I use for gig more. Other than the parameter and its gradients and I would like to know what happened like a cause loss for gig because that's the first step I can decide if something is wrong in a script like I can remove and don't necessarily need to use that for gig.

##### **Qazalin** [[00:25:37](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1537)]
Okay.

##### **Geohot** [[00:25:39](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1539)]
Yeah, I think I think we can get to a bunch of like rewrite rules here that are aware of the length of that edge. There's all sorts of things I'm sure we're saving more than we have to and again, more on that. This is the trade off between recomputation and locality and tiny grad is definitely opposed to recomputation. But this is costing us locality and that's what costing us that's what's all the RAM. Usage I think so I think once we have a good way to visualize it will be able to see what the rules we need are and then add them.

##### **Geohot** [[00:26:21](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1581)]
Yeah, I think we first need to tell certain behaviors happening before we can decide what to do is let's be a great yeah. Okay, let's move on to drivers. Yes, so.

##### **Nimlgen** [[00:26:46](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1606)]
So yes, so for the USB GPU I'll take a minute and share the repelling. Or yeah, so for and we so I merged it last week. So we should have 49 to working with our driver. So the performance is not great right now. Yeah, I'll work on this this week and 59 days well.

##### **Geohot** [[00:27:21](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1641)]
Are you sure the only problem is the huge pages.

##### **Nimlgen** [[00:27:26](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1646)]
Yeah, I mean, performance is not that bad. Like it's not really bad. It's bad, but not really mostly we have a lot of problems with Python because of the we use small pages and because of that we should allocate more. So yeah, it takes a lot of Python time.

##### **Geohot** [[00:27:49](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1669)]
You're talking about huge pages on the GPU side like putting huge pages in the page table on the GPU. Okay. Does AMD have this only in video.

##### **Nimlgen** [[00:28:01](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1681)]
Oh, we support this on AMD.

##### **Geohot** [[00:28:04](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1684)]
I see so we have it on AMD. We just don't have it on a video. Yeah, it makes sense.

##### **Geohot** [[00:28:14](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1694)]
Yeah, so I think not quite yet, but what I see kind of so I think there's there's wrapping up this Nvidia project. There's that COVID support. But then the big project I see you working on pretty much for the rest of the year is just going to be. At my 300X, whatever we can do to get more performance from it better scheduling of the transfers.

##### **Geohot** [[00:28:39](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1719)]
Yeah, all that kind of stuff. The wait once. What? Also wait moving, moving, wait.

##### **Geohot** [[00:28:50](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1730)]
Yeah, yeah, yeah, like like like moving ways more optimally. And then also maybe potentially doing the aql thing or figuring out what we're going to do about the about the XCD sync. Yeah, just like moving weights from drives figuring out why that's slow being able to like.

##### **Geohot** [[00:29:12](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1752)]
Yeah, just figuring out what the fastest ways to schedule these things are.

##### **Geohot** [[00:29:18](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1758)]
Yeah, yeah, I mean, hopefully this is a place where our driver can really start to shine. And we can decide also if we want to do if we want to bypass AMD GPU for the MI 300 or not. Does it look pretty heavy looked at all does it look similar or does it look?

##### **Nimlgen** [[00:29:38](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1778)]
Yeah, I mean, it's similar. The only thing which like it will be. So the only thing that just missing is that we need like at four loops because like XCDs. It's like different GPUs and they also set up like different GPUs. So we just need to add this logic or why she affects nine similar. Yeah, I mean, it's pretty similar to I think this I think this will just come down to wherever we can get.

##### **Geohot** [[00:30:12](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1812)]
You know, just just to follow the performance gradient wherever we can improve performance. I mean, yeah, pretty much our whole goal as a company for the next year. It's going to be to get maximum performance out of this ML per thing. And that's kind of it. If we can do large LLM training as fast as Nvidia can. That's the that's the biggest demand application. Now, but yeah, I mean, I like I like the idea of first getting the MVPCI project wrapped up and making sure that the abstractions we're working with are capable of. I think you can choose between whether you want to prioritize the video decoder stuff or whether you think there's stuff that we can start doing on the AMD stuff earlier.

##### **Geohot** [[00:31:07](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1867)]
By the way, I saw you fix the STMA over around issue. What was that? Basically, we couldn't.

##### **Nimlgen** [[00:31:23](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1883)]
So we have. So yeah, it seems like we generate a lot of copy comments right now. And we simply didn't have any logic to just kind of wait until everything is processed in this queue. So yeah, I mean, it's. But basically in short, like we had more comments than the Q size. And yeah, because of that, we just cannot see to all of them. So now we just can wait for this.

##### **Geohot** [[00:32:07](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1927)]
Yeah, I mean, I see I see I see the spin weight that was added.

##### **Nimlgen** [[00:32:13](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1933)]
Yeah, I mean, actually, I think that's I don't really like that because maybe we should. I know if it's a bad idea to have like environment wearables again to to set the queue sizes. But I think yeah, we should not stall there and wait and for a queue like.

##### **Geohot** [[00:32:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1956)]
How big is the queue right now? 16 makes. Go make a bigger. Yeah, sure.

##### **Geohot** [[00:32:46](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1966)]
I mean, is this some like is this something where if we make it 32 mags, it's fixed or if we make it 32 mags, it's just a bigger problem.

##### **Nimlgen** [[00:32:55](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1975)]
No, I mean, it's I mean, it's fixed for the current workload. But generally, I think we can. We can have the same problem. Yeah, maybe a lot of.

##### **Geohot** [[00:33:07](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1987)]
Yeah, I mean, I see, I see, you know, line 409, which is doing the spinway. And I just, I just see that. I see it getting stuck there. And then that becoming really hard to debug.

##### **Nimlgen** [[00:33:18](https://www.youtube.com/watch?v=U-UYchhy_dY&t=1998)]
Yeah, and yeah, and also the. Yeah, maybe maybe a good idea to a time out there, but also the problem is also only with its day make you because. We do not support like indirect comments on these only on aim this is they make you. So yeah, and because of that, I just can overrun not all other cubes because they launched in the indirect manner.

##### **Geohot** [[00:33:52](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2032)]
Sounds like we should.

##### **Nimlgen** [[00:33:54](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2034)]
Yeah, yeah.

##### **Chenyu** [[00:34:01](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2041)]
I mean, basically for me, because I will be running a bunch of testing testing smaller model training stuff. I will keep posting in the channel for any if you would like to. Do let me know if you want me to run some other diagnosis scripts in case anything bad happened. I for now, I just look at the message and post what's there.

##### **Geohot** [[00:34:29](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2069)]
Yeah, basically that's. The information we can currently collect.

##### **Geohot** [[00:34:40](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2080)]
Sounds good. Okay. Anything else?

##### **Geohot** [[00:34:49](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2089)]
Okay, let's move on to.

##### **Chenyu** [[00:34:52](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2092)]
Can you.

##### **Wozeparrot** [[00:34:53](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2093)]
Not much from you this week. I was out last week this week. I would just try to get tiny.

##### **Wozeparrot** [[00:35:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2100)]
I'm the goal for this week. I guess if you be in has anything. I'm going to upload.

##### **Geohot** [[00:35:08](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2108)]
I upload. Lama wait. We should be able to try fetching the Lama wait from the files. I don't know. The big one is pretty big. Maybe it's using like the wrong like a llama one. So is it all solved like what side's going to do the hashing?

##### **Geohot** [[00:35:41](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2141)]
Yeah. We don't want the client side to do the hashing.

##### **Geohot** [[00:35:46](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2146)]
Yeah, our big first milestone for this is getting is moving. We have two provisioning machines now.

##### **Wozeparrot** [[00:35:55](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2155)]
So much stuff off of those.

##### **Geohot** [[00:35:57](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2157)]
Yeah, no more.

##### **Wozeparrot** [[00:35:58](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2158)]
They're just. Great boxes now. Yep. Oh, you've already moved everything to get. Or just fix it. Basically everything else is just off those are on the provisioning OS. Those are just rate boxes now.

##### **Geohot** [[00:36:11](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2171)]
Great. Let's get rid of them.

##### **Geohot** [[00:36:13](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2173)]
They're ugly in that room.

##### **Chenyu** [[00:36:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2176)]
So we have two more red boxes to say.

##### **Geohot** [[00:36:19](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2179)]
Oh, no, they're not red boxes. In fact, one of them is the only blue box we have. One of them is the blue box and one of them is has two broken 4090s.

##### **Chenyu** [[00:36:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2191)]
Maybe they are using their last strip of magic.

##### **Geohot** [[00:36:35](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2195)]
Yeah.

##### **Qazalin** [[00:36:37](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2197)]
Okay.

##### **Geohot** [[00:36:38](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2198)]
Yes, I don't want to blue box custom one off. No, we never sell custom one off things. You guys are going to post the play.

##### **Geohot** [[00:36:47](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2207)]
Uh, okay.

##### **Chenyu** [[00:36:51](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2211)]
Okay, that sounds good. Next. Z3 symbolic or anything else.

##### **Geohot** [[00:37:02](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2222)]
Like those you're working on. We can't hear you if you're talking. Hi, can you hear me now? Yes, yes.

##### **Sied Lykles** [[00:37:27](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2247)]
Okay, so yeah, so this week I've been working mostly on the view. I'm going to go to the view. Constra factor. Um, that's in place last week or from the new father. It's like fuzzing individual rewrite rules. And then I have some little works is want to make it like into a nice. Oh, that's easy to use if you have a new rule. You want to try. Also, I switched and for further individual rules, I switched to like a bit factor of father, which is a bit slower, but it also tests for like overflow and. Also the div and the more is a bit nicer because it's closer to like the Z3. Bit factor div is actually like truncating the vision. So that's nice.

##### **Geohot** [[00:38:28](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2308)]
How much slower is bit vector versus the like int symbolic hours of stuff?

##### **Sied Lykles** [[00:38:35](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2315)]
Well, so the problem with the bit like the inspector stuff is that it's scale very boiling with the size of your variable. So like one of your links in your expression is going to be some kind of like the fine bar or whatever. And that the fine bar is quite small. Then I get only a few bits basically. Then it's very fast or it's almost equally as fast. But. If you get something else, it gets exponentially slower with. The side of your define bar so if you have you want to put in 32 bits. I get quite slow with the individual stuff that the skill thing you want to do. The individual stuff skills with. Your mom of.

##### **Geohot** [[00:39:27](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2367)]
That makes sense. I mean, my dream is eventually to like move this away from an SMT. And then we solve our like Z3 and to like a sat solver like pico sat and do the lowering in tiny grad.

##### **Sied Lykles** [[00:39:45](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2385)]
Yeah, we would have did like a stop.

##### **Geohot** [[00:39:49](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2389)]
Yeah, like we have basically I don't think we ever have to write a sat solver. I think that's ridiculous. But if we switch to I do think it might be worth writing the the basically the definitions of what each of these things are. Because we have we have these things now. It's like add. Well, what does admin we can actually expand that into a bunch of Boolean operations in a graph. That's. Maybe squared from multiply.

##### **Geohot** [[00:40:21](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2421)]
Really not for division or might be painful, but. Yeah, I mean.

##### **Sied Lykles** [[00:40:29](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2429)]
I mean, that's basically doing that. For the. What is doing.

##### **Geohot** [[00:40:37](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2437)]
Right, like, but it's Z3 is doing this somewhere under the hood. I don't know how to write a divider. I don't know how to write a divider in terms of Boolean logic. But if it's a divider by like a fixed number, I'm sure that's pretty easy and. All that kind of stuff. So yeah, you could have rewrite rules that can rewrite everything into. Dety bull.

##### **Geohot** [[00:41:01](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2461)]
Yeah.

##### **Geohot** [[00:41:03](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2463)]
I don't know how you thought this is a project, but I'm definitely interested in it.

##### **Sied Lykles** [[00:41:10](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2470)]
I mean, where would you use that.

##### **Qazalin** [[00:41:17](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2477)]
Checking.

##### **Sied Lykles** [[00:41:18](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2478)]
They also that is would get slower.

##### **Geohot** [[00:41:21](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2481)]
I mean, we'd use it for two things. So there's a whole wouldn't actually use it to render things. We could use it for verification. But then we could also use it to render to FPGA back ends. Like we could render the whole. We could render a neural network into Boolean logic. I was talking to some kind of Twitter about this about how basically like. As these d types become like what is FP4? It's almost easier to write FP4 as Boolean logic than it is to write it as anything else. Yeah, and then to like re re extract from the Boolean logic. What the what like the system is. I don't know. It's just an interesting place that we can lower and raise from.

##### **Qazalin** [[00:42:13](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2533)]
Yeah.

##### **Chenyu** [[00:42:15](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2535)]
Specifically for the view, Kong's thing. I saw Croslinghouse, Locklaponte and replied to. In the P.O. already. So I was. For the first two.

##### **Sied Lykles** [[00:42:28](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2548)]
Yeah. And just the one thing I always from that is that it's fine. And there's no more false folding in the big graph.

##### **Geohot** [[00:42:42](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2562)]
Right. Wait, why is there no cons folding in the big graph?

##### **Qazalin** [[00:42:47](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2567)]
Because you pass the bar to match right.

##### **Geohot** [[00:42:54](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2574)]
Wait, huh?

##### **Sied Lykles** [[00:42:57](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2577)]
I mean, all the rules, like all the symbolic rules, they have you pass the C bar. Which matches either it belongs to or. Metric ones, but if you have a cons with the view on top.

##### **Geohot** [[00:43:11](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2591)]
Well, yeah, you have a. No, it should still work. Okay, so what should happen is this? Um, const, if it had if I can't, I added a rule to ST. Whereas const on a shape. Has has. Ask. Const on device has a shape of zero dimensions. So there should definitely still be.

##### **Geohot** [[00:43:45](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2625)]
I can't hear you. Oh, um, can you hear me now?

##### **Sied Lykles** [[00:43:53](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2633)]
Yeah, you just. I'm telling you out sometimes.

##### **Geohot** [[00:43:57](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2637)]
So there definitely should still be cons folding on the big graph. And the way that it should work is you want to move the views right. Right. So a const has a shape of a zero dimensional, just like an empty topple. If you have an empty topple, like there shouldn't be a view. There doesn't always have to be a view on a const. There only has to be a view on a const if it has a shape, if it's expanded. But if you have two cons that are added together, the views should move right across that ad. Uh, we might have to add that view moving right to the, uh, to the big graph. But we absolutely still need constant folding in the big graph. Do you see what I mean? How to do it?

##### **Sied Lykles** [[00:44:38](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2678)]
Yeah, yeah. I don't think we can't do it with spotted. Yeah.

##### **Geohot** [[00:44:44](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2684)]
Um, yeah, I mean, it's not look. If we don't have it, it's not, it's not the end of the world. But we should definitely be able to add it back by moving views right. Uh, and having the default shape of a const be back, back, back.

##### **Sied Lykles** [[00:44:58](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2698)]
Yeah, we're going to turn it on.

##### **Geohot** [[00:45:01](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2701)]
Cool. Yeah, just move it. If, basically, if you have, if you have a binary op, which has two identical views on it, uh, that are expansive views, those views should be move right. That's a universal rule. Same thing with a unary op. Yeah, if you have expansions before the op, then they should move right.

##### **Sied Lykles** [[00:45:23](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2723)]
Well, I mean, well, if you have like, x plus 1 and x is a load, or even have x is an expansion,

##### **Geohot** [[00:45:33](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2733)]
then you still move the one,

##### **Sied Lykles** [[00:45:37](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2737)]
where the x plus 0, because you want the one 4 is 0.

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2741)]
Well, 0 can just, 0 can always just go away. Um, and, oh, I see. So you're saying, like, what do you do about the plus 0? Because there's a view there that's doing an expand.

##### **Sied Lykles** [[00:45:57](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2757)]
I mean, yeah, if it's not, if it's not, there's no mod, then the shape can just be whatever.

##### **Geohot** [[00:46:04](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2764)]
Well, the shape has to be a real shape. I mean, it does have to match, uh, I guess the plus 0 is a different case from the cons folding. But for like, the cons folding for like one plus two, it should move a views right and then, and then do the cons fold using the normal rule.

##### **Geohot** [[00:46:23](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2783)]
Yeah, I mean, no, to be used to get that.

##### **Geohot** [[00:46:26](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2786)]
Yeah, I mean, it's also it's not like cons folding is a lot of rules. I don't know, but I'm not.

##### **Sied Lykles** [[00:46:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2791)]
There was some problems like it.

##### **Geohot** [[00:46:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2796)]
And I know how it's fine. Yeah, I can do that.

##### **Geohot** [[00:46:39](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2799)]
But I, if you want to take it out for now, I'm okay with taking it out.

##### **Chenyu** [[00:46:47](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2807)]
Yeah, let's just be, try to be practical and not to be blocked too much by some of the rarely seen in real life test cases. If you think it's like not necessary, you can find to remove. But do think about it and think about like what needs to be done if you want to like support later.

##### **Geohot** [[00:47:13](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2833)]
Anything else?

##### **Geohot** [[00:47:17](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2837)]
Thanks.

##### **Chenyu** [[00:47:20](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2840)]
Okay. Let's move on to our next. Oh, our next we merge. I forgot this week or last week.

##### **Chenyu** [[00:47:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2856)]
I emerge all the all the refactoring stuff on the type. So now the flow 16 is correctly parsed as flow 16. And the D type foldback is so much. So the current situation is we have the previous open pilot test. Previously, we were using flow 32 full a model and flow 32 forward and put data. Now the behavior is we use flow 16 for the model and flow 32 for the data. Because for flow 16 model, flow 16 data, there's just weird mismatch compared to on XMOT. How many miracle issue not like.

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2902)]
Doesn't like the models wrong, but it's just if it's bigger. So I think that's fine for now.

##### **Chenyu** [[00:48:33](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2913)]
The other issue that was brought out many times was low test, like this.

##### **Geohot** [[00:48:39](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2919)]
Not clear why.

##### **Geohot** [[00:48:44](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2924)]
Yeah, if you want to load the whole model, if it's if it if your shirts fixed by something like moving the whole model to like CPU or Python, that's fine. And let's just get that fixed. I shouldn't make it much lower. Might even make it faster.

##### **Chenyu** [[00:49:01](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2941)]
There was a draft the R on this. I think a slightly slower. But it's not too much. I think using pythons fine. Yeah.

##### **Geohot** [[00:49:14](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2954)]
Yeah, CPU is less recommend because CPU might have more reflectors down the lines.

##### **Chenyu** [[00:49:25](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2965)]
Okay, I mean, basically, you can first reproduce this fairly consistently. Then you propose a fixed that looks fine and you fix the scenario you reproduce. And I think it's good.

##### **Geohot** [[00:49:45](https://www.youtube.com/watch?v=U-UYchhy_dY&t=2985)]
I'll choose your original thing for me. No, yeah, yeah, basically. Okay. Let's move on to local. Hi.

##### **Ignaciosica** [[00:50:05](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3005)]
Well, three things for me first is that I rebased the PR to a cleaner approach. After all the factors that have been taking place in kernel.py. And realize and that. Secondly, I. I open SAP yard to fix the gate on group store because I think the I explained it the PR, but I think the the gating is pretty aggressive on locals. And it's it's not general enough to work on. On locals. So yeah, basically getting a decade pushing only for group stores right now. And also I started a. The factor for yellow for red feedback on on the one is.

##### **Geohot** [[00:51:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3060)]
Yeah, I see that they use order decked. Why not just use kernel info, right? Like kernel info is the right place to track this stuff. Every time we do a transformation, it's bad.

##### **Geohot** [[00:51:15](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3075)]
Transformation.

##### **Geohot** [[00:51:17](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3077)]
So.

##### **Geohot** [[00:51:21](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3081)]
Right. So the thing that we're eventually returning from the kernel class is this data class called kernel info. And can we just use kernel info to track everything?

##### **Geohot** [[00:51:38](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3098)]
Well, I see.

##### **Geohot** [[00:51:40](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3100)]
So eventually where I see this going is that all of the information about the. Opt ops is contained in kernel info. And then kernel info is this is this arg on the sink, which contains all the stuff that tells the lower. How to how to actually do the optimizations. I could also see that kernel info being put on contiguous is. And that will let us specify from the top level tensor graph. How to actually do stuff. But yeah, the yellow thing it needs to be a simplification. If it ends up being more lines, we don't want to.

##### **Ignaciosica** [[00:52:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3136)]
Yeah, yeah, I agree. But it's I think it's multi stage because it's address like many things. At the same time. So yeah, in the end, I think it will be. My. Readable, I think, but yeah.

##### **Geohot** [[00:52:41](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3161)]
But yeah, what I would do instead of this order deck thing is just create create the kernel info. In. Yeah, but.

##### **Geohot** [[00:52:54](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3174)]
Yeah, I mean, it was to save the. Or ticked as a topple for kernel info.

##### **Geohot** [[00:53:05](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3185)]
Are you saving in kernel info, but I see you have global local reduce upcast. You can just have. Okay, I have have four properties on that class. We already have most of them.

##### **Ignaciosica** [[00:53:17](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3197)]
You know, I know that for now, I like, I tried to left everything as it was before and all the other. This thing. In order to make all the offset calculations. More straightforward. But. Yeah, that's. Like right now, the offset calculations are like for each one of the different access. It's like a different algorithm, different way of calculating the first. The offset and the income.

##### **Geohot** [[00:53:54](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3234)]
No, yeah, I agree. I agree that it's ridiculous, but I look at like things in your refactor like line 139 and line 142 where you have properties that are returning these self access things.

##### **Ignaciosica** [[00:54:05](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3245)]
Instead of that, I only add them in order to not have to change the test and the heuristics in this PR. I agree. Like only to keep the changes in kernel that I this are going to.

##### **Geohot** [[00:54:19](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3259)]
Yeah, yeah, where I would go with this is like eventually what's going to happen with kernel.pi. Like don't add new code to kernel.pi. Like adding a new thing called an order deck does not what we want to do. You kernel.pi is eventually going to basically become kernel info. Like there's going to be some function that transforms your opt-ops into a kernel info. And that function can the function can be a beam search that function can be a heuristic that function can be anything. That function could just be a straight up parser of a bunch of opt-ops. But yeah, like the closer we can get kernel.pi the more logic we can basically copy from kernel.pi into kernel info, the better.

##### **Geohot** [[00:55:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3300)]
Okay.

##### **Geohot** [[00:55:08](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3308)]
I mean, I could see a world where good optimized as T just literally sticks the kernel info on the sink. It's just it's just sell that as T that replace our equals kernel info.

##### **Geohot** [[00:55:20](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3320)]
That's very cool.

##### **Chenyu** [[00:55:21](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3321)]
You can just change some stuff in the kernel info.

##### **Geohot** [[00:55:27](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3327)]
Hopefully lower will work. Yeah, and no, but the best part is going to be when you can do contiguous. We have to unify contiguous and g-barrier. But once we unify contiguous and g-barrier, you'll just be able to do dot contiguous or dot contiguous backward with the kernel info at the highest level. And then that kernel info will propagate all the way down. It'll go to the scheduler and it'll propagate to to the lower where it actually applies those optimizations. And that looks a lot like how haylight does it.

##### **Chenyu** [[00:56:03](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3363)]
Okay. Let's go through all of on these repy fire style starting with red.

##### **Wozeparrot** [[00:56:10](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3370)]
Not a whole lot of dates. I think I'm pretty much done with the rewrite. I'm just going to do the correctness check. I think I kind of said that last time, but that's still in progress on that part. Is it faster? I haven't done the pull run yet because I was just doing the correctness check still. I still have one, I think one line that's rewrite. It's like an arcsword. I think at the very end that the original script does. So I just need to make sure that that's correct. It was our source.

##### **Qazalin** [[00:56:45](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3405)]
Okay.

##### **Chenyu** [[00:56:45](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3405)]
I don't know if it's faster by at least 10 years. And you can come play more.

##### **Wozeparrot** [[00:56:52](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3412)]
Okay.

##### **Chenyu** [[00:56:55](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3415)]
I don't see you again here. There are a bunch of discussion on the cloud sync stuff. I trust George or words parades someone knows this stuff. Refactors. I think it's mostly pick.

##### **Geohot** [[00:57:19](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3439)]
Yeah, I mean, we're working on our factors. I don't know. Refacture.

##### **Geohot** [[00:57:29](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3449)]
I locked the constant for us like ease. Yeah, that one is locked. The contiguous G barrier one should be pretty easy to. If someone here wants to look at one, moving the old is before the red dims is pretty hard. The unifying the load store thing is super hard. Merging assigns store should be a bunch of PRs that migrate assigned to store.

##### **Chenyu** [[00:58:00](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3480)]
Yeah, I think you understand one difficult part for this is like figuring out the correct order to stuff. And if you split into multiple.

##### **Geohot** [[00:58:12](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3492)]
Yeah. If someone's interested here and trying to refactor bounty, the contiguous G barrier one is very doable.

##### **Geohot** [[00:58:23](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3503)]
Why is the barrier not the contiguous to Star Wars?

##### **Geohot** [[00:58:28](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3508)]
Yeah, it was just easier to refactor. It was just easier to make it a different op just so they wouldn't interfere and I could add it as a separate thing. That's like, yeah, we have a bunch of legacy rules for that. And the merging assigned into store. I would start with I will lock the bounty for someone if they can do the first thing to do is to replace a sign and the in the tensor. Dot pie level with store and then to replace the things in the scheduler with store. You can do that that part should be pretty easy. The hard part is going to be dealing with like C style. C style is is has a different semantics for assigned and store. That's going to be more annoying.

##### **Qazalin** [[00:59:16](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3556)]
I'm going to gate these doors on the index.

##### **Geohot** [[00:59:21](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3561)]
Pardon me?

##### **Qazalin** [[00:59:22](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3562)]
The gated assign.

##### **Geohot** [[00:59:27](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3567)]
What's gated assign?

##### **Qazalin** [[00:59:29](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3569)]
The gated stores.

##### **Geohot** [[00:59:31](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3571)]
What's a gated store? You mean with an if statement or you mean with an index that doesn't mask?

##### **Qazalin** [[00:59:36](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3576)]
If statements.

##### **Geohot** [[00:59:38](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3578)]
Oh, yeah, I mean that's. If statements are wrong. If statement shouldn't be a. Yeah, yeah, that's that's that's annoying. Everything that's in like the C style level and that level, it's going to be really annoying to unify assigned and store. But you should be able to pretty easily do the top level one. I can't apply.

##### **Geohot** [[00:59:58](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3598)]
Sorry, tensor.py and the scheduler.

##### **Chenyu** [[01:00:05](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3605)]
There are those reflectors. Finally, SVG and C4 torch backend. George came in test leads to. The lock them both. I think it looks fine. If it. It's fine to do. I think it's okay.

##### **Geohot** [[01:00:19](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3619)]
Great. Yeah.

##### **Geohot** [[01:00:20](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3620)]
I can test. If you want to.

##### **Chenyu** [[01:00:22](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3622)]
I just test it. I think we can conclude leads to it's not our top priority, but. The work is done. It's not too big for us to maintain anyway.

##### **Geohot** [[01:00:35](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3635)]
Oh, the guide one.

##### **Geohot** [[01:00:38](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3638)]
Okay, did that finally come through? I feel like I tried it and it didn't work, but I'll try it again.

##### **Chenyu** [[01:00:48](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3648)]
Yeah, so both of those recent updates. I think that's the only kind of all story was keeping like merge master into their print. I think it's probably on the list.

##### **Geohot** [[01:01:01](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3661)]
I see. And then the SVD one. Oh, good. There's some benchmarks. Are they reasonable? Oh, they're insane.

##### **Chenyu** [[01:01:12](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3672)]
The code has a lot of eyes and a range and stuffing it. But. Yeah. The glorify example. It's something. Yeah, I'm okay with that. So I just take a quick look to see if there's anything obviously wrong otherwise. I think it's. Well there.

##### **Chenyu** [[01:01:42](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3702)]
Okay. That's it for this meeting. Thank you, everyone. And we'll see you next week.

##### **Geohot** [[01:01:52](https://www.youtube.com/watch?v=U-UYchhy_dY&t=3712)]
Bye.
