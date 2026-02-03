# 2025-10-20 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time, 9pm Hong Kong time
- company update
- bye bye ShapeTracker
- usb gpu https://x.com/__tinygrad__/status/1980082660920918045
- multi output kernel
- rangeify regressions, openpilot, resnet, bert
- FUSE_OPTIM, assign?
- more cleanups?
- viz
- driver
- tiny kitten
- more symbolic?
- other bounties, new linearizer, new clang2py

### Audio

[Youtube Link](https://www.youtube.com/watch?v=rt8wGfaM1y8)

### Highlights

- **[Company Update](#geohot-000007)**: Three TinyBox orders were received over the weekend, though payment is still pending. There are seven units in stock, and a dev box with 5090s is being set up.
- **[Bye Bye ShapeTracker](#geohot-000129)**: ShapeTracker has been completely removed. The main remaining issue is the Torch backend, which relied on it heavily, but fixing it is low priority as it was slow and likely unused.
- **[USB GPU](#geohot-000332)**: A new driver allows using external NVIDIA or AMD GPUs on Mac/Linux via Thunderbolt. Kernel execution speed is identical to native, with data transfer around 3 GB/s, making it a convenient tool for local development.
- **[Multi-Output Kernels & Flash Attention](#geohot-000576)**: Work is underway to support multi-output kernels, which is crucial for optimizing models like LLaMA 405. This enables recomputing intermediate tensors (like in Flash Attention backward) to save memory, a task dependent on the new linearizer. A new `ops.after` has been introduced to better manage dependencies.
- **[Rangeify Regressions](#chenyu-001041)**: Significant performance regressions have been observed after the rangeify merge. Openpilot models are much slower, ResNet is 3x slower, and BERT is 2-3x slower on MI300x. Fixes are dependent on the new linearizer and resolving bugs in BEAM search.
- **[FUSE_OPTIM](#chenyu-001588)**: An optimization from Torch, FUSE_OPTIM merges optimizer parameters into a single tensor. It is now faster in tinygrad but has a bug in `assign` causing silent correctness issues that needs to be fixed before it can be enabled.
- **[Code Cleanups](#geohot-001849)**: Following the removal of ShapeTracker and other major refactors, there are more opportunities for code cleanup, such as unifying buffer uops and removing unused functions from `ops.py`.
- **[Visualizer (Viz) Improvements](#geohot-001893)**: The kernel visualizer has become much more readable post-rangeify. It can now hide complex indexing logic, presenting a cleaner and more understandable graph of operations.
- **[Driver Updates](#nimlgen-002131)**: Nimlgen is working on several driver issues, including a Mac hardware crash when unplugging the USB GPU, the NVIDIA 50-series reset bug (blocked by a new `clang2py`), and a QCOM driver refactor to support textures.
- **[Tiny Kitten](#wozeparrot-002703)**: The effort to port Thunder Kittens' Flash Attention to tinygrad's UOps is underway. Progress is currently blocked by NVRTC's lack of C++20 support. The "flat" nature of UOps makes translation less direct, sparking discussion on better ways to represent tiled algorithms.
- **[Symbolic IR and Loop Transformations](#sieds_lykles-003206)**: Sieds is working on advanced symbolic transformations like "additive loop splitting" and moving `reduce_collapse` to the higher-level graph. This will enable more generic and powerful optimizations.
- **[Bounties Update](#chenyu-003635)**: Several bounties are seeing good progress, including float8 support, the Winograd rewrite rule, and a new version of `clang2py`. The new linearizer is close to being merged but first needs a hang and a BEAM search bug to be fixed.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=0)]
Let's get started. How was the company update?

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=7)]
We supposedly sold three Tinyboxes this weekend.

##### **Geohot** [[00:00:10](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=10)]
I don't know if we've gotten the money for any of them yet.

##### **Geohot** [[00:00:16](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=16)]
We sold..

##### **Geohot** [[00:00:18](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=18)]
No, we're not ready to announce that yet, but we sold those and we got those shipped.

##### **Geohot** [[00:00:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=23)]
So yeah, money's coming in. We got three orders, but nobody's paid for them yet.

##### **Chenyu** [[00:00:33](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=33)]
Yeah, I realize there's not many sales in the past two or three weeks.

##### **Geohot** [[00:00:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=39)]
Yeah, well, we had the big sale. Okay. And we can announce that at some point.

##### **Nimlgen** [[00:00:48](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=48)]
Cool.

##### **Geohot** [[00:00:51](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=51)]
We have seven in stock, ready to go. I think we have GPUs for 11. Great. Are you going to put some in CI? Should we? They're expensive. Or at least some for DevMachine. Yeah. Well, how many do we want? We want three, right?

##### **Chenyu** [[00:01:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=83)]
No, no, no. For DevMachine. Probably one. We only have like one green box now.

##### **Geohot** [[00:01:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=88)]
Oh, we can do that. I have one in my office, but it has two 4090s in it. We can definitely put the 5090s back in that one and take it as a dev box.

##### **Nimlgen** [[00:01:37](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=97)]
Yeah.

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=99)]
Yeah, I'll be back in San Diego in two weeks and we can set them up. Yeah, we should have some for green. We should have some for development. At least one. That should be us.

##### **Chenyu** [[00:01:55](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=115)]
Hey, uh, so Texas with delete Shape checker, the tracker has gone. Yeah. RDC goodbye to check.

##### **Nimlgen** [[00:02:08](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=128)]
Yeah.

##### **Geohot** [[00:02:09](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=129)]
That's just talking with Amanda about this. If there's some way I got, like, could have we known? shells knowing that it? Was dumb.

##### **Geohot** [[00:02:26](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=146)]
Nope. I think in the parallel universe that can work.

##### **Geohot** [[00:02:31](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=151)]
It's going to be so infuriating when we finish TinyGrad and it's so simple and everyone's just like, wow, I could have written this in like a week. Why did it take you guys so many years? Like, well, yeah, because you read this one, you could write it in a week.

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=167)]
Yes.

##### **Chenyu** [[00:02:49](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=169)]
I don't know, I mean, there are also other framework doing their thing, right? It's like people inspire each other and people collaboratively figure out the frontier.

##### **Geohot** [[00:03:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=183)]
Yeah. Is there any other known issue from removing

##### **Chenyu** [[00:03:14](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=194)]
ShapeTracker?

##### **Nimlgen** [[00:03:16](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=196)]
Oh.

##### **Geohot** [[00:03:17](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=197)]
I know. I disabled the Torch backend. The Torch backend used it in a bunch of places and the places that it used it in, it doesn't have to. Someone just needs to like spend some time thinking about how Torch's storage system actually works and how we want to interface with it because it was just kind of hacks.

##### **Chenyu** [[00:03:40](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=220)]
Torch center, a lot of things are wrong as strided.

##### **Geohot** [[00:03:44](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=224)]
Yeah, I mean, there's nothing really wrong with as strided. We can still like decompose as strided into movement ups.

##### **Geohot** [[00:03:55](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=235)]
Oh. That should totally work. That code should still work. Okay.

##### **Chenyu** [[00:04:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=243)]
I don't know. So what is Torch?

##### **Geohot** [[00:04:06](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=246)]
Oh, so we used it in a bunch of places to like initialize the, so the Torch tensors all have shape and strides. Yeah. And we used it in a bunch of places to like initialize the stuff, like the strides of the Torch tensor.

##### **Geohot** [[00:04:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=268)]
I don't know. Someone just needs to like look at it and put a few hours into it and I'm sure they can fix it.

##### **Nimlgen** [[00:04:34](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=274)]
Okay.

##### **Chenyu** [[00:04:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=275)]
How important is this?

##### **Geohot** [[00:04:38](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=278)]
I don't know. I don't think anyone was using it. No, because it was very slow. Yeah. I don't know.

##### **Nimlgen** [[00:04:46](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=286)]
I don't think anyone was using it. I don't know. I don't think anyone was using it. Yeah. I don't think anyone was using it.

##### **Geohot** [[00:04:54](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=294)]
So let's shape checker.

##### **Chenyu** [[00:05:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=303)]
Next we have USB GPU. I just included it here because we made an announcement. What's the state if you want to just announce this to us? Okay. So you're just going to have to go to the group in this meeting and what's the next for this?

##### **Geohot** [[00:05:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=323)]
Let me switch to my other microphone. Maybe that will work better. I think this microphone has some noise. Okay, cool.

##### **Geohot** [[00:05:32](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=332)]
Yeah. So USB GPU works. You can try it. If you have a Mac and or Linux, anything with a Thunderbolt, basically, it should work with like anything with Thunderbolt and anything with a Linux. Yeah, if you have a Thunderbolt dock and you plug a GPU in. I'd be curious if someone could make it work on Linux. I think it should just pretty much work. But we have a driver for Mac. So set SIP on your Mac, turn SIP off, and then install the driver.

##### **Geohot** [[00:06:05](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=365)]
And then, yeah, you can use NVIDIA GPUs or AMD GPUs from your Mac. So running the kernel should have the same speed? Oh, the tweet forgot the tap step.

##### **Geohot** [[00:06:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=390)]
Good point. People figure that out. Yeah, running the kernel should definitely have the same speed. The kernel should be exactly the same. For copy in and copy out, I'm getting like three gigabytes per second, which should be pretty fast.

##### **Geohot** [[00:06:49](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=409)]
But if you copy the whole memory, it takes eight seconds on a 49ID.

##### **Chenyu** [[00:06:53](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=413)]
So are there more things to do with this? Or do we want to promote this? Or will this become another? Something like Torch from N that seems to be nice, but no one really used?

##### **Geohot** [[00:07:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=443)]
Oh, this one I think we'll use. I mean, I think we'll use it internally. Like, I'm excited to do development from my Mac just connected to a GPO. What's the difference between that and use another machine?

##### **Geohot** [[00:07:45](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=465)]
Yeah, SSH2. You have the machine still in effort.

##### **Chenyu** [[00:07:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=470)]
Is it low? Okay. You need to bring the setup with you. But okay. I guess that works.

##### **Geohot** [[00:07:58](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=478)]
Yeah, but no, I mean, I already have a GPU. I don't know. We have a bunch of GPUs around. It's nice. It just plugs into your computer. You can edit the one thing. You don't have to agent forward. You don't have to VS code forward. You don't have to deal with whatever weird stuff's on the remote system. Also, if you want to power cycle the GPU, you can actually just power cycle the GPU. It's pretty convenient.

##### **Chenyu** [[00:08:20](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=500)]
Does it support multi GPU?

##### **Geohot** [[00:08:24](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=504)]
I don't know. Maybe. I don't know if we have two GPUs to try it. It's a lot of GPUs. Oh, I bought three docs and three 40, 50, 60s, which are coming to the office. But in retrospect, I wish I bought 40 60s because we have to see if the reset issue is fixed.

##### **Chenyu** [[00:08:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=527)]
Oh, should it be fixed on 40 60s later?

##### **Geohot** [[00:08:52](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=532)]
Oh, 40 60s don't have it. It's only on the 50 series. I see. Yeah.

##### **Geohot** [[00:09:02](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=542)]
The 50s have like this. They got rid of this loader. There used to be this like loader for the GSP and you could always like, but now the loader is gone. It's just the GSP.

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=553)]
So I don't know. But hey, the USB GPU people give you the try.

##### **Chenyu** [[00:09:25](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=565)]
We can move on to next. I just go to the multi output kernel. I don't know what to call flash attention backward or the thing you're working on.

##### **Geohot** [[00:09:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=576)]
Yeah. So there's a few problems with flash attention backward now. Not even the one not the one with the online range. That's a different problem, but just getting the outside of kernel. So getting the memory buffer is all correct. So there's two problems right now. Flash attention works flash attention has the right inputs and outputs, but flash attention backwards doesn't and it's for two reasons. One, it doesn't know that it has to recompute the the score matrix. So like that outer product Matrix is recomputed in both the forward pass and the backward pass. So it's pretty easy to write the rule to do this. You can look at the ratio of loads to stores. So if you have something that has like the flash attention kernels, I'm looking at have a ratio of 32x more stores than loads and you can kind of just say, okay, if it's like 10x more stores and loads, then you probably want to recompute this kernel instead of storing it. So I can do that. But then the axis order just due to how the reduces are numbered. The axis order isn't very good. So that requires linearizer improvements, which is mostly just a new linearizer. So then you start thinking about the new linearizer and you realize the new linearizer. The key to the linearizer is like so it's kind of related to multi-opper kernels too because the key thing about multi-opper kernels. Is that two stores share the same end range. If you want two stores to be in the same loop, they have the same end range, but we don't really support this right now. Right now, we assume that every range has a single Terminator, which is nice, but doesn't work for a multi output. So you want to add end range to the kernel graph. But then you realize that in order to do that, we should really do a good job. Cleaning up how we order dependencies, right? So right now I would just have the stores hanging off of the loads. So today I added ops.after ops.after. We should start documenting these ops better too as these things start to Yes, please.

##### **Chenyu** [[00:12:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=723)]
Yes. Yes. Yes. Yeah,

##### **Geohot** [[00:12:05](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=725)]
I put some dogs. Yeah, there's a comment on top of ops.after. But it basically ops.after. The first argument to ops.after is a buffer. And then the second argument, is anything you want. And it promises you that it will give you that buffer after the second argument runs. So like if you want to, and I've refactored a whole bunch of stuff. I refactored like the initializer of reduces. So in the initializer of reduces, you want to set it to zero, but you want to set it to zero before you first use it. So you can do that with after.

##### **Chenyu** [[00:12:41](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=761)]
Oh, does that fix the sign?

##### **Geohot** [[00:12:44](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=764)]
Well, there's no more sign. Well, what do you mean by fix the sign? So a sign isn't used anymore in the in the kernel graph. It never really was a sign. It's actually just after.

##### **Chenyu** [[00:12:56](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=776)]
I mean, there are some known issues with the sign. Does this fix that?

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=782)]
I don't. I'm not aware of the known issues. Okay, I will let you know later. Cool. But no, I mean, my goal isn't to fix the sign. My goal is to is to migrate basically to new linearizer. And I found a really interesting bug. I found the bug that's in the new linearizer and BEAM. It turns out BEAM will silently skip kernels if your compute estimator is wrong. So that's what was causing that issue with the linearizer.

##### **Geohot** [[00:13:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=816)]
But yeah,

##### **Geohot** [[00:13:38](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=818)]
so what I can do what I can do tomorrow, I can take a day and I can tighten up the specs of a whole bunch of ops. So for example, like loads can no longer have more than one argument. I like it was it was kind of ridiculous how we just had like three arguments on load sometime. We've made a lot of progress on this. This isn't just like something that I can do today out of nowhere. A big reason that I can do this for example is because now we have a good understanding of how invalid works. Like invalid is a is a is a is a part of the argument.

##### **Geohot** [[00:14:15](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=855)]
Part of the index. Yeah, so yeah,

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=864)]
upstart after leads to multi output and multi output and that other rule and fixing a loop ordering should be everything we need to get flash attention backwards to be good. So yeah, should be by the end of the week. And then I think by the end of this week or next I can have LLaMA 405 be using a reasonable amount of memory. Even if the with null equals one, even if the kernels are still unreasonable.

##### **Chenyu** [[00:14:58](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=898)]
Okay, so no context length square basically,

##### **Geohot** [[00:15:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=903)]
you know, more context length squared use of memory.

##### **Geohot** [[00:15:05](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=905)]
Yeah, great. Okay, that sounds good.

##### **Chenyu** [[00:15:15](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=915)]
Oh, and there is a real substitute and there is a P contiguous.

##### **Chenyu** [[00:15:20](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=920)]
That's a new flex.

##### **Geohot** [[00:15:22](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=922)]
Yeah. Okay, so real substitute just doesn't use the substitute up. It uses actual substitute.

##### **Sieds Lykles** [[00:15:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=930)]
I just remove that actually real substitute. Oh, it's gone. Did you fix the bug? I just put like a gate on the substitute. Like, you know, how to have to open store. The gate.

##### **Geohot** [[00:15:45](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=945)]
Yeah. Okay.

##### **Sieds Lykles** [[00:15:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=947)]
It's just when you do the substitute, you don't want to take the total storage on the whole graph, the whole big graph. So if you just gate the substitute, then it's like an outs faster than it's like an actual substitute and it's faster than

##### **Geohot** [[00:16:07](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=967)]
the substitute thing. Cool. Nice. Good line deletion. Hey, no real substitute. Yay. And the P tongue cake is just the range of I to

##### **Geohot** [[00:16:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=995)]
peek and take his range of fight to get stands for partial contiguous. Yeah, it's a it's a development flag, but it's a lot better than flags like fuse a range and fuse calm backwards. Why did we have a flag that mentioned calm? An a range. What are those things? Those things are nothing.

##### **Geohot** [[00:16:59](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1019)]
They're just reduces. Pekin takes a real thing. A poorly named real thing, but real. It's fine. Cake. Let's talk about some of the rangeify regression still.

##### **Chenyu** [[00:17:21](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1041)]
The biggest one is open pilot. So Harold and I will merge will update some of the benchmark to be the latest model. So currently comma can update tiny great version because the significant regression in model speed. I should be able to see that in benchmark with putting the new model and I think in one. of the PR head also put the pre-rangedified numbers. And he's basically saying we need to get a number back to that number so they can upgrade. I think one might be, so OpenPy has two models now, two main model. One is the vision and one is a policy. I think the vision model, I tried messing around with the older disable block reorder kind of fix the speed, even make it faster. So I don't know if it works. We should just remove block reorder. It's very hard to work with now.

##### **Geohot** [[00:18:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1108)]
We're going to merge the new linearizer soon anyway.

##### **Chenyu** [[00:18:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1110)]
Yeah, so I think hopefully with a new linearizer, we can remove block reorder and hopefully that fix the vision model.

##### **Geohot** [[00:18:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1119)]
Yeah. The.

##### **Chenyu** [[00:18:41](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1121)]
I think the issue was if I just disable it, now some other model has rendering issue.

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1130)]
Yeah, the Qualcomm compiler is really crappy. Yeah, anyway.

##### **Chenyu** [[00:18:59](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1139)]
The other one is I think a policy model, the speed. So I think it was like 3 milliseconds and now it's 6 or something like that. And it's due to one reduced kernel, probably the reduced. So the loader is bad or something like that. The reduced kernel itself took like 2.5 milliseconds.

##### **Geohot** [[00:19:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1163)]
So fixing that should also fix the speed regression here. Otherwise, all the kernel seems to be bad.

##### **Chenyu** [[00:19:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1176)]
We wait for the new linearizer and see if I can do anything with the reduced or reduced loader and hopefully that's it.

##### **Geohot** [[00:19:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1187)]
Yeah, hopefully it's just linearizer stuff. I mean, there's another thing Steve and I were talking about, about the cat kernel being slow.

##### **Chenyu** [[00:19:57](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1197)]
Oh, yeah. There was a heuristic that tried to always upcast your cat

##### **Geohot** [[00:20:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1203)]
kernel. I mean, we were looking at also, you

##### **Sieds Lykles** [[00:20:11](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1211)]
know, splitting the cat loop. So it's not like if you're getting, I don't know, 10 things together, then you're doing 10 different adds, which you don't need to do. Yeah, we're just playing around with range cutting. Yeah, it's a bit tricky to get it rendered out for GPUs. Because, yeah. How the globals work. Yeah.

##### **Chenyu** [[00:20:42](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1242)]
I think the idea initially that upcasting is faster because those plus zero would just disappear. You end up not doing those odd. Here is probably similar.

##### **Geohot** [[00:20:59](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1259)]
I don't know. Can you do a pad when you upcast a pivot?

##### **Nimlgen** [[00:21:04](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1264)]
I'm going to look at the open side.

##### **Geohot** [[00:21:06](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1266)]
Sorry? If you do a pad and do like pad two, then. Yeah. Upcast or local, is that faster? I haven't tried that. I don't know. I mean, yeah. There's two cat kernels, I think, and they're both not very fast. Let's see. Yeah, I remember the last one of.

##### **Sieds Lykles** [[00:21:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1296)]
Yeah, the last one, I think, and the very first one are both.

##### **Chenyu** [[00:21:41](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1301)]
My impression is that one probably can be made faster. But that one is also not that slow. It's just I don't know why. Still good, you have.

##### **Chenyu** [[00:21:53](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1313)]
OK.

##### **Chenyu** [[00:21:54](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1314)]
So that's open pilot. Comma really wants to upgrade, keep fresh TinyGrad from deviating too much. So let's prioritize this. The next is ResNet. I think ResNet is 3x slower compared to pre-range. And part of it is because the count backward is slow. And it's probably the same slowness as before. That's probably why use count backward was another thing.

##### **Geohot** [[00:22:29](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1349)]
Is that 3x slower with BEAM or without BEAM?

##### **Chenyu** [[00:22:32](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1352)]
With BEAM, it's very slow.

##### **Chenyu** [[00:22:38](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1358)]
Bless that. BERT. Interesting. I think BERT on Green Machine is slightly faster than before. That's good. BERT on MI300x is slower. It's 2x, 3x slower. And part of it is because I post this in the BERT MLPF BERT channel. For some reason, the Python time grows with GPU counts. And I don't know what's happening or if you have any guess.

##### **Chenyu** [[00:23:15](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1395)]
This is only on MI300x, not on small tiny bugs.

##### **Geohot** [[00:23:24](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1404)]
Any other idea?

##### **Nimlgen** [[00:23:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1410)]
So the only difference is that MI300 is AQL. And there is no bind. I can function for AQL. So I know I'll need to look into that. Maybe there are a lot of kernels, and that's why it's slow.

##### **Geohot** [[00:23:52](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1432)]
Oh, yeah. There's definitely a lot of kernels. So you're saying you can't bind the buffer and do it indirect?

##### **Nimlgen** [[00:23:57](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1437)]
Yeah. AQL doesn't support indirect buffers.

##### **Geohot** [[00:24:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1443)]
Hmm.

##### **Nimlgen** [[00:24:04](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1444)]
Yeah.

##### **Chenyu** [[00:24:10](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1450)]
I'll just leave this here. And I think some other slowness might be due to the same thing that estimate is wrong. So the 1000x of thing is wrong. I will try to relax that and test again. Maybe it's that.

##### **Geohot** [[00:24:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1468)]
Yeah. I mean, the estimate thing is specifically broken by my PR. I don't know. I'm going to fix that and put some better tests on it. But I don't know. The Python time thing, the AQL thing makes total sense to explain that. And I mean, sure, it's worse, but it shouldn't really explain why it's so slow.

##### **Chenyu** [[00:24:48](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1488)]
Yeah. So I think the big slowdown is probably just on TensorFlow or some kernel. I'll take a look. I will try to relax everything around BEAM.

##### **Geohot** [[00:25:01](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1501)]
Well, so more than relaxing things around BEAM, it took me like an hour to figure out what was going on, because none of the flags printed anything about that kernel that was being filtered out. Like I said, BEAM debug, I said BEAM strict. Yeah.

##### **Chenyu** [[00:25:19](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1519)]
I don't know. Let's let's let's we can check who put this in first place. No, no, no.

##### **Geohot** [[00:25:27](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1527)]
Well, I'm just saying we should spend time adding a little bit of I'll document the UOps.

##### **Chenyu** [[00:25:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1535)]
Yes. Okay. I understand. Yes.

##### **Geohot** [[00:25:38](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1538)]
That's sweet.

##### **Chenyu** [[00:25:40](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1540)]
Yeah. No, I agree. I think we also removed some of the BEAM debug flags a while ago when we do a clean up. Now we are back to optimizing for speed. We should add this back and hopefully we'll have a better understanding, maybe in terms of the tools or some kind of stats at the end of the BEAM to at least know maybe what's the portion of the kernels that we skipped because of early files. I think that's likely that can help.

##### **Geohot** [[00:26:11](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1571)]
Yeah, I agree.

##### **Nimlgen** [[00:26:13](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1573)]
Cool.

##### **Chenyu** [[00:26:14](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1574)]
Yeah. That's the regression I'm aware of. I think there might be some other like more things. Let's just a smaller version of this. But let's try to get this fixed.

##### **Chenyu** [[00:26:26](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1586)]
Okay.

##### **Chenyu** [[00:26:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1588)]
Next one is views optin. So for people in this channel, use optin is a flag that basically. It's an idea that just put all your optimizer internal parameters into one big tensor and you just always work that big tensor. If after then you split that into like individual small pieces.

##### **Geohot** [[00:27:01](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1621)]
So I just stole this idea from Torch. It's just in Torch and it works. Yeah. It's fast now too. I added contiguous to the grants and that made it fast. It should be faster.

##### **Chenyu** [[00:27:11](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1631)]
Yes, I think it's faster. But there's a problem. If you try to enable it, there's a bug in the assign that the output would be silently different. And I can fix it by adding realize in the assign line. But that feels very wrong.

##### **Geohot** [[00:27:29](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1649)]
Yeah, we definitely should do that. If you can show me bugs in assign, I'll fix them. I know how to fix them now.

##### **Chenyu** [[00:27:34](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1654)]
Oh, I have the. I'll give you a for repro. I have the snippet posted somewhere.

##### **Geohot** [[00:27:45](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1665)]
Yeah, if you can, if you can isolate bugs in assign the new stuff, it's so easy now. Like, it took me so little time to like add after and like I can make changes now and nothing's fragile and nothing breaks. Excited.

##### **Chenyu** [[00:28:01](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1681)]
Okay.

##### **Geohot** [[00:28:01](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1681)]
I'll post that. I'll post that. Like when I made all those changes last week to the movement ops, there would have been no way to do that in the old stuff. Every time I would change stuff, just things wouldn't work and I'd have no idea why they didn't work and everything was so fragile. Now I make a change and it's like, no. Okay, cool. Yeah, that's kind of all that I expected. Okay, those two tests don't pass. I see why. Great. I fix that.

##### **Geohot** [[00:28:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1703)]
Great done. Great.

##### **Chenyu** [[00:28:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1708)]
Yeah, I think aside from that, that's the sign case. Cool. Everything else is just a matter of updating the test. I don't know what's up with muon and fuseoptim, but let's fix the issue first and see if the muon asserts don't use fusearrange. Oh, sorry. Oh, muon?

##### **Geohot** [[00:28:49](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1729)]
No, muon just can't use fuseoptim because it's two-dimensional.

##### **Geohot** [[00:28:55](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1735)]
Muon is shape-dependent. So what Torch does for this is it fuses all the tensors that have the same shape. Same shape, or you just need the same dimension on one of them or something like that? I'm not sure exactly what it is, but that's why fuseoptim doesn't work. Yeah.

##### **Geohot** [[00:29:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1763)]
It's not a bug in fuseoptim. It's just like..

##### **Chenyu** [[00:29:25](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1765)]
No, no, because I tried it. It doesn't work. It doesn't work. And if I remove the assert line, it runs. It's just the outputs are different.

##### **Geohot** [[00:29:32](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1772)]
Well, yeah, that's why the assert's there. Interesting. It's not supposed to work. You can't fuseoptim on Vue run. It's a function in the algorithm. Okay.

##### **Chenyu** [[00:29:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1790)]
Anyway, let's fix the known issue first and then decide if we want to enable that to true by default then.

##### **Geohot** [[00:29:57](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1797)]
Yeah, I think we can make it true by default except for muon.

##### **Chenyu** [[00:30:00](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1800)]
Yeah, but I mean, what if people use this to write a new optimizer and they are not aware of that this thing can be enabled or not? And the output would be different.

##### **Geohot** [[00:30:11](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1811)]
Yeah, then maybe we just make it the default for like the new optimizer.

##### **Chenyu** [[00:30:16](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1816)]
I think for the known optimizer that this works, make default for that, but globally maybe not as defined. We can decide later. Okay. Next is.. So we deleted a bunch of stuff, all the scheduler, all the shape checker, whizzler, some of the views.

##### **Chenyu** [[00:30:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1839)]
After rentify, is there any other known cleanups that we should be deleting?

##### **Geohot** [[00:30:49](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1849)]
There's some minor things. There's like a.buff uop and.buff and.buff.

##### **Geohot** [[00:30:59](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1859)]
There's like three of them and they're all slightly different. I think they can be unified into one thing and understand actually what that is now. I think I'm doing a big one now with all the after stuff. And then I can.. What I'll do also after I'm done with the after stuff is I'll tighten up all the specs. And then we can just go through the ops file and I bet you there's a whole bunch of functions on there that aren't used anymore. Just delete them. Oh, like I can do just like..

##### **Nimlgen** [[00:31:32](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1892)]
Yeah.

##### **Geohot** [[00:31:33](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1893)]
Yeah. Yeah. No. It's so readable now. Also we put some stuff in viz today, which you can click the view range stuff and we hide all the indexing. So it actually looks very readable. Like the vizs are very readable when after rentify.

##### **Nimlgen** [[00:31:51](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1911)]
Okay.

##### **Chenyu** [[00:31:53](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1913)]
Cloud link is not here. Would I hurry to find? She might be in the office.

##### **Chenyu** [[00:32:00](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1920)]
Express listing is unreadable. Yeah. I'm disappointed.

##### **Geohot** [[00:32:06](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1926)]
Wait, is she in the office?

##### **Nimlgen** [[00:32:08](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1928)]
Yeah.

##### **Geohot** [[00:32:10](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1930)]
Oh, no. I mean, like right now.

##### **Chenyu** [[00:32:13](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1933)]
Yeah. Not right now. Maybe it's better now.

##### **Geohot** [[00:32:16](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1936)]
Oh, no.

##### **Sieds Lykles** [[00:32:18](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1938)]
She's not here.

##### **Geohot** [[00:32:19](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1939)]
Oh, she's not here. Okay. I'm there.

##### **Chenyu** [[00:32:24](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1944)]
Okay. No, that's good. Yeah. Let's do more cleanups and see where we are. I definitely don't see my line count going down.

##### **Nimlgen** [[00:32:33](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1953)]
I'm not sure.

##### **Geohot** [[00:32:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1955)]
Well, that's kind of expected. Well, whatever. Yeah. I don't know. The lines are the lines are more readable now. I've been writing in less of a line cramp style. Yeah, I don't know. What is this? Is the line count really is it going up?

##### **Chenyu** [[00:33:12](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=1992)]
I think we certainly have. So now I think now the style. So we are kind of moving. So we previously have a styles that has one big function that does ten different stuff like a linearized function or something that function does ten things in one function. That's really bad. And now things got broken into. I don't know if they have any more functions. I don't know. I'll try to use smaller functions with their rewrite rules. And it's much harder to know if those small functions are like the much.

##### **Geohot** [[00:33:42](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2022)]
No, the line counts way down. We merged nir.

##### **Geohot** [[00:33:46](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2026)]
Nir was huge. And I was a ton of lines. Nir is about 500 at most.

##### **Geohot** [[00:33:53](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2033)]
More I think.

##### **Chenyu** [[00:33:54](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2034)]
Okay.

##### **Geohot** [[00:33:57](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2037)]
Yeah, no wait, the line counts way down.

##### **Chenyu** [[00:34:01](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2041)]
I don't know, it doesn't feel way down when I'm reading files like ops.py or other stuff, but maybe that's because there are things still can be cleaned up, so I would know better after.

##### **Geohot** [[00:34:11](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2051)]
Well, yeah, because we didn't clean up ops.py, we deleted an entire directory and tons of other crap. Shape.

##### **Chenyu** [[00:34:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2063)]
Shape only has like 200 lines, it's very small.

##### **Geohot** [[00:34:27](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2067)]
Wait, okay, NIR is only 295, okay, it's not that many. Yeah, but shape went, the whole directory went away, and all the view pushing stuff went away.

##### **Chenyu** [[00:34:38](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2078)]
Yes, go on, lows have smaller, maybe not that good, but okay, anyway.

##### **Geohot** [[00:34:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2087)]
All right, well, we can make the graph and look at the state of the line crisis.

##### **Chenyu** [[00:34:52](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2092)]
Yeah. Yeah, I have that, it always goes up, so.

##### **Geohot** [[00:34:58](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2098)]
Anyway. The sequence on here, you want to say something about this? No, just let us know when you are talking.

##### **Chenyu** [[00:35:24](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2124)]
Probably, by the time it is ready. And I guess the main issue is, the fact that we're not making any issues on this

##### **Geohot** [[00:35:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2130)]
over here. Right.

##### **Nimlgen** [[00:35:31](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2131)]
Yeah. Making, by the way, a good fetch. crashes is actually a hardware error of the last level cache. And the problem here is that nothing stops Python accessing bar and this memory which is no longer valid and because of that the cache panics. I'll try to do something from the dext. I know maybe I can kill this client. So I don't know. I'll try to do something.

##### **Geohot** [[00:36:21](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2181)]
So you're telling me when you unplug it, the kernel.. Apple's slipping.

##### **Geohot** [[00:36:33](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2193)]
I added the MLX guy on Twitter if there's some way because at least once a day I have to reboot my computer because the Apple GPU goes into some state where it's drawing 50

##### **Geohot** [[00:36:42](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2202)]
watts even though I killed the process. I mean, it's not that bad. You just have to know not to unplug it while the Python is on.

##### **Nimlgen** [[00:36:51](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2211)]
Yeah. I'll still check if it's possible to do something like that because some other guys have similar problems on Apple forums. So yeah, I'll check this.

##### **Geohot** [[00:37:04](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2224)]
What I'm really interested in is the reset issue.

##### **Nimlgen** [[00:37:09](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2229)]
Yeah. So for the reset issue. Um.. So for the 580.. Yeah. So for the 680, I think you just have to do something with the I think we need the new clang 2.0. The problem there is that NVIDIA just changes structs from version to version and they actually require the exact match of the driver, GSP and user land. And even now we do not support like the.. Opsenv doesn't support like CUDA 13 of these. I don't know what they're doing. I think it's 580 driver because some structs have changed. So yeah. And I think with the new clang 2.0, we can generate them on the fly based on the version you're using. But currently, yeah, if we regenerate it, we'll break the old version. Oh, I see.

##### **Geohot** [[00:38:10](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2290)]
So it'll break with the driver. Yeah. With the real driver installed.

##### **Nimlgen** [[00:38:16](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2296)]
Yeah. So yeah. So that's blocked on the new clang 2.0. So of course, yeah, I think with the new clang 2.0, it will be cleaner solution. Of course, I can do something maybe, but I don't know if I should spend time on this now.

##### **Geohot** [[00:38:34](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2314)]
Well, do we have a way to.. Because I want to use these.. I ordered three 5060s for the comma office. And yeah, I don't want to set the model. I don't want to set the top if they're constantly going to be breaking in CI like our 5090s are.

##### **Geohot** [[00:38:51](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2331)]
Do we have a way to send a reset to the dock? Yeah, probably.

##### **Nimlgen** [[00:39:07](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2347)]
I mean, there are some options to do the secondary bus reset for the thunderbolt. So that might work as well. Yeah.

##### **Geohot** [[00:39:16](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2356)]
I think that does work because if I turn the off switch, if I turn the switch to off and then back to on, that works.

##### **Geohot** [[00:39:24](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2364)]
So I don't know what that's doing, but.. Yeah. Okay. We'll take a look into this. Cool.

##### **Geohot** [[00:39:38](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2378)]
I applied for our driver kit thing. I DMed a guy who used to work on the driver kit team. We'll see.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2390)]
I just accepted my computer doesn't accept.

##### **Nimlgen** [[00:39:54](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2394)]
Yeah. So that's foreign. So for QCOM, it kind of works, but actually the new thing they started to use, I don't know if it's a new compiler, maybe it's in the new hardware. So actually they started to replace some buffers with textures. And that's.. So yeah, that's the main difference, which requires some refactors in QCOM.

##### **Geohot** [[00:40:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2430)]
Interesting. So they'll just silently replace a buffer with a texture.

##### **Nimlgen** [[00:40:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2436)]
Not.. I mean, not silently. Just.. Yeah. So it's not like a.. It says this in the binary that it will be submitted as a texture and not a buffer.

##### **Geohot** [[00:40:48](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2448)]
How does it know the length? Sorry, can you repeat? How does it know the length?

##### **Geohot** [[00:41:00](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2460)]
Because when you have a texture in OpenCL, you have to give it a size.

##### **Nimlgen** [[00:41:05](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2465)]
Yeah. You should submit size. But actually, it's not 2D texture. It's like a special texture underscore buffer. But yeah, you still need to submit size. And actually, yeah. And actually, even a simpler, which is like null simpler, kind of.

##### **Geohot** [[00:41:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2483)]
I mean, it makes sense why they do this. Only the textures have the L1 cache. And yeah, I want to do the refactor where we move away from having images exposed in the front end.

##### **Nimlgen** [[00:41:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2495)]
Yeah. But still strange. They do this not for all kernels. Like, some kernels use that, and some kernels use buffer. So..

##### **Geohot** [[00:41:44](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2504)]
You know, they wrote an if statement. They love if statements at Qualcomm.

##### **Geohot** [[00:41:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2510)]
Think about it. Now they can employ two people. Do we know what's up with AnyMech1?

##### **Chenyu** [[00:42:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2523)]
So I was debugging C4. So I update the OSP. I update the OS version to the latest in 14. And USB start to fail.

##### **Nimlgen** [[00:42:14](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2534)]
Yeah. So actually, it returns like something not expected for use BGP for, like, leap USB error code, which is 99, which is, like, OS specific. So I don't know. Maybe we can try. I just tried to reset the USB. But I haven't found any good way. I think I can use it on Mac to do that and reset. And resets didn't help either. So maybe we can try to replug this for USB. But yeah, the return code is somewhat strange.

##### **Chenyu** [[00:42:55](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2575)]
So I should just ask in the office to unplug it and plug it back?

##### **Geohot** [[00:43:02](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2582)]
Yeah. Wait. Rebooting the computer doesn't work? No. Yeah. Huh. Interesting. Yeah. So yeah, it can't even open the USB. Yeah. Maybe it's just in support state. Well, we got some other comma.

##### **Chenyu** [[00:43:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2608)]
I probably stopped the GitHub action listening thing. But now the OpenSC cheesecake is settle. Really? and we haven't changed anything about how it works in the flush, which would be good for small nodes. But I think Tidemech does so very well.

##### **Chenyu** [[00:43:53](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2633)]
Yes.

##### **Wozeparrot** [[00:43:57](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2637)]
It Pln was great.

##### **Geohot** [[00:44:05](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2645)]
Interesting. OK.

##### **Chenyu** [[00:44:10](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2650)]
I mean, if some machine is not used in the past, I don't know, three days, we probably want to mark it. Otherwise, we will never know if some machine suddenly goes down, other than things become slower to connect.

##### **Nimlgen** [[00:44:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2668)]
OK.

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2670)]
Anything else for driver?

##### **Nimlgen** [[00:44:34](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2674)]
No. So probably this week also we'll do the SQTT for GFX 9.

##### **Geohot** [[00:44:42](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2682)]
Yeah, I heard also that there was some issue with needing AM reset after SQTT.

##### **Geohot** [[00:44:52](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2692)]
Yeah, and probably look into that. Yeah. Cool. Next. This is Tiny Kitten.

##### **Wozeparrot** [[00:45:03](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2703)]
So I started porting the Flash Attention example over. The Thunder Kittens Flash Attention example, at least currently, we can't compile with NVRTC

##### **Geohot** [[00:45:17](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2717)]
because a lot of the C++ headers are missing. Well, you probably just include them, right?

##### **Wozeparrot** [[00:45:25](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2725)]
No, this is just an NVRTC thing. Like a lot of the Thunder Kittens requires C++ 20. And a bunch of the newer stuff that NVRTC just doesn't have. NVCC has it. And NVRTC doesn't.

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2739)]
You want to just add a 10 line OS.System compiler?

##### **Wozeparrot** [[00:45:43](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2743)]
Yeah.

##### **Geohot** [[00:45:45](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2745)]
Yeah. I'm just going to do that. Yeah, that works. I made a channel for Tiny Kittens.

##### **Nimlgen** [[00:45:55](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2755)]
OK.

##### **Geohot** [[00:45:56](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2756)]
Yeah, I saw that. The way that I would probably go about this is just I would write, like, a whole bunch of, oh, by the way, I was reading Tiny Kittens this weekend. Yeah, it's the craziest C++ 20 stuff. You ever heard of concepts? No. Yeah, I saw that. I was like, oh. Well, it doesn't look like any C++ I've ever really read before.

##### **Wozeparrot** [[00:46:17](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2777)]
Very new.

##### **Geohot** [[00:46:17](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2777)]
I mean, some parts make sense. But like, yeah, it's not. But so what I would do probably is just write some really small samples in Thunder Kittens. Just look at the PTX. And then get Tiny Kittens. And then figure out that matches them.

##### **Geohot** [[00:46:33](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2793)]
OK. Oh. Yeah, I mean.

##### **Chenyu** [[00:46:38](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2798)]
I mean, I'm reading the Wikipedia. If this concept is just constraint on types for templates, that seems good.

##### **Geohot** [[00:46:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2810)]
Yeah, sure. It's a constraint on types for templates. Sounds good. I know vaguely what a template is. It's like when you have a std vector string.

##### **Geohot** [[00:47:01](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2821)]
Yeah. Yeah. Interesting. Cool.

##### **Wozeparrot** [[00:47:11](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2831)]
I have some comments on my initial porting. It definitely feels more annoying to write in UOps just because everything is so flat. What do you mean by that? Because essentially you translate, you almost translate all the for loops into ranges. And your code ends up being very flat.

##### **Geohot** [[00:47:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2856)]
So another thing that you could do instead of translating the for loops into ranges is you could create a tile D type and then write a lowering step. Like that might be what it ends up looking like. Like UOps have hierarchy, but the hierarchy is expressed through a hierarchy. So it's not just through lowering, not through scoping.

##### **Geohot** [[00:48:05](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2885)]
Yeah. Yeah, no, I'm reading what you got here now.

##### **Wozeparrot** [[00:48:18](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2898)]
Yeah, I mean. Not entirely sure how to express yet.

##### **Geohot** [[00:48:25](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2905)]
Like the. So. Wool loads. Which loads? Like the pipeline loads.

##### **Geohot** [[00:48:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2916)]
Yeah, so I have an example of that in the AMD fast map mall, though it's just pipelined in registers.

##### **Geohot** [[00:48:46](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2926)]
But you can also use you can use dot after now. Oh, I also have actually I wrote all of pipelining.

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2936)]
I actually have working pipelining in the. In like the. The main stuff too. But so what you can do is you can use use dot after. And then you can like get the buffer. So you want to do the like you have to type it out manually, but you want to do the initial one before the for loop and then do the.

##### **Geohot** [[00:49:26](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2966)]
The next one after the for loop and so on and so forth. Okay.

##### **Nimlgen** [[00:49:31](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2971)]
How to type in, um.

##### **Geohot** [[00:49:32](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2972)]
Let me find.

##### **Geohot** [[00:49:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2975)]
I did right. Pipelining.

##### **Chenyu** [[00:49:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2979)]
Well, that's. What about maxing out memos on seven?

##### **Geohot** [[00:49:44](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2984)]
100 of the X. I have a handwritten example to do that.

##### **Nimlgen** [[00:49:59](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=2999)]
And you just have to type into the vchr eud file to use that I did.

##### **Geohot** [[00:50:04](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3004)]
That's all written with pre.. It's all written..

##### **Geohot** [[00:50:06](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3006)]
That example that I posted is all pre-after. But the idea is that you basically have, like, four loads in computes, and then you put the.. You, like, change the order to be, like..

##### **Geohot** [[00:50:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3035)]
But, yeah, so I have that matmul maxed out. At least as much as you can without going to assembly. Yeah, so, like, what I just posted in TinyKittens is what pipelining is.

##### **Chenyu** [[00:51:19](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3079)]
And with after, this would be just a chain of after and this, like, specific order you want?

##### **Geohot** [[00:51:27](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3087)]
Yeah, so sort of. I mean, what you can do with after is..

##### **Geohot** [[00:51:31](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3091)]
No, maybe.. Yeah, you can definitely do this with after. It's not really designed for it.

##### **Geohot** [[00:51:49](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3109)]
After more talks about.. So the idea with after is buffers are mutable. So.. When you're.. Say your load depends on a buffer. Well, yeah, but when does it depend on the buffer? All right, so that's why you have after. After says you're doing that load after something else already happened.

##### **Geohot** [[00:52:18](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3138)]
What if you don't put after?

##### **Chenyu** [[00:52:20](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3140)]
Is it just, like, not guaranteed?

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3143)]
Yeah, it could go either direction. It's just a top of sort. So if you just have, like.. So say you have, like.. Like.. Yeah, just the simplest case. You have a store to a buffer and a load from a buffer. So normally, if you have a load dependent on the buffer and a store dependent on the buffer, the top of sort does not guarantee which order it's going to put them in. But if you promise you can do both things, you can either do the load before the store by saying you want the store version of the buffer to be after the load, then you'll guarantee that the store happens after the load, vice versa.

##### **Geohot** [[00:53:02](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3182)]
Okay. Let's move on. The next one is for C.

##### **Nimlgen** [[00:53:22](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3202)]
Hi.

##### **Geohot** [[00:53:23](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3203)]
Can you hear me? Yes.

##### **Sieds Lykles** [[00:53:26](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3206)]
Okay. Sorry. Yeah. I mean, things I've been working on are, like, the cat range splitting and also getting the.. moving the reduced collapse to the big graph. And then.. Ideally, like, also replace reduced collapse with, like, a loop splitting approach,

##### **Geohot** [[00:53:56](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3236)]
which would be very generic. But, yeah, I don't know. The cat..

##### **Sieds Lykles** [[00:54:08](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3248)]
I mean, we were just talking.. I was talking to George about.. Also, sort of the algebra of.. Like, when we do an upcast or, you know, reshape, whatever, you change your ranges multiplicatively. So you split them into factors. And then the thing that we don't really do at Diningrad is additive loop splitting.

##### **Geohot** [[00:54:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3279)]
So, for example, we have, like, that too.

##### **Sieds Lykles** [[00:54:51](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3291)]
But we don't have the option to start off part of the range. So that's.. One half of the range is a multiple of, like, 32. Or multiple of 2.

##### **Geohot** [[00:55:08](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3308)]
And then.. And then you have, like, the tail end of the range.

##### **Sieds Lykles** [[00:55:18](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3318)]
So, yeah. Playing a little bit around with that. And the main trick is getting it to render. And also to get the GPU DIMM assigned correctly to that. When you do that. Because GPU DIMM is a little bit tricky.

##### **Geohot** [[00:55:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3339)]
So, I mean.. So, I have an implementation of cat splitting, but it only works on CPU.

##### **Geohot** [[00:55:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3347)]
I can help you with the GPU DIMM thing. If you just get it merged for CPU. Just, like, only enable that pass on things that don't have.. Like.. Like.. If ops local is off. It's kind of related to the stuff I'm doing. I mean, GPU DIMMs will not scale to, like.. Like, GPU DIMMs is not..

##### **Geohot** [[00:56:12](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3372)]
That needs to be upgraded a lot. Yeah. Like, right now, it's just a bunch of hacks.

##### **Sieds Lykles** [[00:56:22](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3382)]
I mean, GPUs.. You can also.. We can also make, like, triangular cuts. So, with GPU DIMMs, I mean, they have to be rectangular. All the cuts you do. With..

##### **Geohot** [[00:56:39](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3399)]
Yeah.

##### **Sieds Lykles** [[00:56:41](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3401)]
On CPU, you can.. I don't know. Especially with something like A-range folding. I wouldn't do.. I wouldn't do any..

##### **Geohot** [[00:56:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3410)]
I would not do any triangular stuff.

##### **Sieds Lykles** [[00:56:56](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3416)]
I mean, yeah. I might do them in the A-range folding. And only keep it if it folds. So, you don't really have.. You know. If you don't have any triangular cuts. But..

##### **Geohot** [[00:57:06](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3426)]
Oh, I see what you're saying. Oh, I see. Oh, the A-range folding is a triangular cut. I understand.

##### **Geohot** [[00:57:13](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3433)]
Yeah.

##### **Geohot** [[00:57:16](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3436)]
Yeah. Yeah. Maybe we could always just have something that, yeah, rejects it. If after the simplification, it's left with a triangular loop.

##### **Sieds Lykles** [[00:57:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3448)]
Yeah. Yeah. Yeah. Yeah. So, a triangular cut, we can just always..

##### **Geohot** [[00:57:33](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3453)]
We're trying to.. Go ahead. Go ahead. No, I want to talk about something else.

##### **Geohot** [[00:57:45](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3465)]
Oh, I guess, like, some form of triangular cuts are okay. Yeah. But, no, I mean.. GPU is just hard to optimize.

##### **Geohot** [[00:57:56](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3476)]
That's a cool.. I like this language. Triangular cut. rectangular cut. That makes sense.

##### **Chenyu** [[00:58:04](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3484)]
I have a comment on the reduce collapse, since you are working on that. So I was trying to, so because there are one function called reduce and parent it, and there is one that's another thing. And I was trying to remove the alignment.

##### **Chenyu** [[00:58:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3508)]
Yeah, yeah. I was trying to remove, oh, is it gone already?

##### **Sieds Lykles** [[00:58:41](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3521)]
Yeah, I replaced one of them with the other.

##### **Chenyu** [[00:58:45](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3525)]
Yeah, yeah. OK, great, because I was testing that. And also, I was trying to just comment it all rules inside p and reduce collapse. And I was trying to remove the alignment, because I was interested to know what, if any, if every one of those are used. And oftentimes, I can get all the tasks to pass. But if I look into the underlying kernels, things would be different. So if you also notice things that are working on this area, I think it would be nice to have more robusted test case against it.

##### **Sieds Lykles** [[00:59:28](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3568)]
I mean, yeah, I fixed, like, I changed one of the rules. And then that fixed one in A range in, like, LLaMA. If you see on Benchmark, there's, like, a really big drop on LLaMA, because it had some A range. But yeah, that one is not in the test.

##### **Chenyu** [[00:59:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3590)]
Yeah, usually, there is a problem if we can remove rules and all the tests pass. But this subtly breaks something else. And I feel like let's simplify and, like, folding places, like, one of those. And this is bad, because it made it very hard to iterate and try to, like, merge rules or change stages, because these, like, hidden things. So ideally, those should be captured more explicitly.

##### **Geohot** [[01:00:25](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3625)]
Yeah. I'll try to get more tests. Sounds good.

##### **Chenyu** [[01:00:35](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3635)]
A lot of time. So let's quickly go through other bounties. I know there's also a float8 support from B1DG.

##### **Chenyu** [[01:00:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3647)]
I think I commented on one of it to ask if you have any speed.

##### **Geohot** [[01:00:54](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3654)]
How fast is it? Yeah.

##### **Chenyu** [[01:01:08](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3668)]
So you can see the speed here. Overall, I think the speed issue is just, like, good to have included in your PR so at least people can reproduce and try to run it and see what's the state. But it can be separate from, like, optimizing the speed to be optimal. Just making sure it's calling the correct instruction and outputs are correct.

##### **Geohot** [[01:01:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3690)]
I think that's good to merge a little PR. And another big piece is a new linearizer.

##### **Chenyu** [[01:01:43](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3703)]
Are we ready to merge that?

##### **Nimlgen** [[01:01:46](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3706)]
No.

##### **Geohot** [[01:01:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3707)]
So there's that BEAM bug, which I'll fix tomorrow.

##### **Geohot** [[01:01:54](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3714)]
But yeah, then I think we're getting kind of close. I think there's a few other things on it.

##### **Geohot** [[01:02:07](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3727)]
Oh, apparently it hangs sometime. There's also a few failures of the tests. It hangs if things can't be generated. OK. That's really bad.

##### **Geohot** [[01:02:26](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3746)]
Yeah, yeah, yeah. The hanging needs to be fixed. I said it should never hang. It should detect this failure case like the old one. But yeah, otherwise I think it's pretty close. The other bounty I'm excited about

##### **Geohot** [[01:02:40](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3760)]
is the Winograd rewrite rule bounty.

##### **Chenyu** [[01:02:47](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3767)]
Is that close?

##### **Geohot** [[01:02:50](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3770)]
Bankminer70, is it close? Uh.

##### **Geohot** [[01:02:52](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3772)]
Uh. No. No, I think there's a bunch more work to be done. But there's a reason it's an $800 bounty. There's a bunch of cleanup to do on this. But the idea is basically right. Yeah, and then we can like, yeah, Winograd doesn't have to be a tensor level flag. We can Winograd anything.

##### **Chenyu** [[01:03:17](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3797)]
Mm-hmm.

##### **Chenyu** [[01:03:20](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3800)]
We can also Winograd different size.

##### **Chenyu** [[01:03:22](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3802)]
Yeah. This is only one of it. This is Winograd 3x2. We have like 2x2, 3x2.

##### **Geohot** [[01:03:30](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3810)]
Yeah.

##### **Geohot** [[01:03:31](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3811)]
There's something in there called Miracle, and it's printing Miracle. So there's still a lot of work to do.

##### **Geohot** [[01:03:36](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3816)]
But yeah. OK.

##### **Geohot** [[01:03:40](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3820)]
Oh, Miracle. Miracle, yeah, Miracle shape. Great. There's also a bounty to put.

##### **Chenyu** [[01:03:53](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3833)]
It's a one 2 pi or something entry.

##### **Geohot** [[01:03:57](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3837)]
Oh, yeah. I'll lock that. OK. There's some good progress on that. Oh. That's good. We're getting some bounties again. Yeah. We've got a bunch of bounties. Yeah. I add you speaker for the next meeting. Chrisann. Again, just for the next meeting, I think it'll probably be when we're about ready

##### **Geohot** [[01:04:55](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3895)]
to merge this.

##### **Chenyu** [[01:04:59](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3899)]
Sounds good. Okay. Thanks, everyone. That's the meeting for this week.

##### **Chenyu** [[01:05:04](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3904)]
See you next week. Bye bye.

##### **Geohot** [[01:05:06](https://www.youtube.com/watch?v=rt8wGfaM1y8&t=3906)]
Bye.
