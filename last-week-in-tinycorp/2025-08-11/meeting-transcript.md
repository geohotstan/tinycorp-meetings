# 2025-08-11 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company updates
- rangeify
- MLPerf LLaMA (dataloader / eval / MP / grad_acc mem)
- viz tool
- drivers
- cloud
- symbolic
- onnx
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=QmGmVAMdxwE)

### Highlights

- **[Company Update](#geohot-000014)**: TinyBox shipping is slightly behind schedule, but the three pending orders will be shipped this week. Delays are due to rigorous quality testing to ensure the PCIe comes up at 16x.
- **[rangeify](#geohot-000143)**: Significant progress is being made, including a `RewriteNotReady` exception to handle bottom-up rewrites for fusions like FlashAttention. It might be merged this week, after which optimizations like tensor cores will be re-integrated.
- **[MLPerf LLaMA / eval](#chenyu-000530)**: Training loss is decreasing, but the team needs a reliable evaluation script to confirm they are meeting the 5.6 eval loss target. Wozeparrot will focus on building the correct eval script this week.
- **[MLPerf LLaMA / Model Parallel](#chenyu-000746)**: Model parallel code has been implemented and works for the 8B model but is hitting a compiler error on the MI300X for the 70B model, which is now under investigation.
- **[MLPerf LLaMA / Gradient Accumulation](#chenyu-000849)**: The gradient accumulation implementation is causing memory usage to increase with more accumulation steps, contrary to expectations. Geohot suggests JITing a single mini-batch loop instead of the entire accumulation sequence to manage memory and scheduling.
- **[viz tool](#qazalin-001834)**: A performance-improving PR for the timeline view is ready, which will make CPU traces faster and fix zooming issues. A new feature to add vertical markers from Python to the timeline was also requested for easier debugging and will be implemented.
- **[drivers](#nimlgen-003141)**: The CPU has become a bottleneck for data loading in LLaMA. The proposed solution is to implement multithreading for CPU kernels to improve performance.
- **[cloud](#wozeparrot-003750)**: The multi-machine setup will be tested this week to validate the associated bounty and prepare the scripts for MLPerf multi-machine submissions.
- **[symbolic](#sieds-lykles-003823)**: A bug in the Z3 renderer has been fixed, and progress is being made on constant folding. An investigation is ongoing for a hang that occurs during parallel BEAM search.
- **[symbolic / Deleting View](#geohot-004503)**: A new project is to enhance the symbolic engine to handle all logic currently in the `view` module (e.g., merging reshapes), which will allow `view` to be removed in preparation for rangeify.
- **[onnx](#chenyu-004856)**: Cubic support has been merged, while `if` op support is pending a refactor. A persistent segfault, possibly related to Python's `contextvars`, is under investigation.
- **[Other Bounties / MoE](#chenyu-005352)**: The Mixture-of-Experts (MoE) bounty could see significant progress by optimizing the `top_k` function, which is currently very slow. Geohot will investigate fusing it with rangeify.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=0)]
Start with Company Update.

##### **Geohot** [[00:00:02](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2)]
So yeah, we've been working on the secret project for Kama. In the office we have the secret picture of the secret project.

##### **Geohot** [[00:00:14](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=14)]
Yeah, that's nice. I think we're a little bit behind right now on TinyBox shipping. We'll definitely get those out this week. I think we have three pending orders right now. But yeah, we have a bunch.

##### **Geohot** [[00:00:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=31)]
I don't know, we had some issues with bad CPUs or something. Oh no, we do a lot of tests to make sure the PCIe comes up at 16x. There's a lot of things that can prevent the PCIe from being 16x. Loose cable, not seated in the GPU, bad CPU, bad CPU seating, bad mother.. motherboard. So we want to make sure that all the Tinyboxes are really good before shipping. Yeah. And oh, since you guys have all been using the Tinyboxes more in the Tinyroom, they're getting too hot in there. So I bought some fans, some HEPA filters,

##### **Geohot** [[00:01:18](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=78)]
and we'll go in there with some duct tape. Put it all together.

##### **Chenyu** [[00:01:23](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=83)]
Yeah, it's okay. Use TinyBox more. Oh yeah, yeah, use it.

##### **Geohot** [[00:01:27](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=87)]
Oh, by all means, use it. It's not going to break nothing. Right now we just have the windows open, which is fine. But I don't want to get dust in the room.

##### **Geohot** [[00:01:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=97)]
Okay. Sounds good. RangerFi?

##### **Geohot** [[00:01:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=103)]
Yeah, so I think we're finally seeing some good progress on RangerFi. I got the stuff merged yesterday to handle children in a coherent way. So this isn't a problem, really, when you're doing a top. down rewrite, but when you're doing a bottom-up rewrite, you can get to a node that has two children. And what usually happens, the bottom-up rewrite is basically DFS. So it will go through, and it will process the parents before it processes the other branch of the children, which is, in most cases, totally fine. Eventually what happens is that the child branch just.. eventually gets processed. It sees that the parent was already rewritten, and it grabs the parent from the cache. So it's not like it processes it twice or anything. But if you have a context, technically any time you have a context for a rewrite, the cache can be wrong. Because the rewrite rule can be context-dependent. So if the context changes, technically the cache is invalid. But it would be way too slow if we actually did that. So I found a better way to do this, which is you can raise an exception called rewriteNotReady. So if you're on that path, if you're on that path going through and you see that you're about to go to the parent node, you just raise rewriteNotReady in the child, and then it will add that node to the back of the queue. So it'll process up the other thing, and that way you can process both branches before you get back to the parent node. So this is needed for the child. And this is needed for the FlashAttention fusion, where you want to make sure you've processed until you have both indexes ready. And then you can see what you have to close for the indexes. So that's one of the rules. And then I have two other rules. One is about closing ranges inside of.. Basically the ranges have to be a tree. The ranges are not a DAG. Loops cannot be a DAG. Because you can't have anything where.. where you.. like, reconnect them. You can't have diamonds, basically. So it has to be a tree. So one rule is dealing with that, and the other rule is dealing with.. So convolutions, what happens is you have an axis that has two ranges. It's not having two ranges that's bad, but the two ranges are overlapping. So that overlapping is doing recomputation, and you just want to end that axis as soon as you see that there's recomputation about to be done. You don't have to, but.. Like, that's the.. The heuristics that I'm trying to put in rangeify say do not do recomputation, basically.

##### **Geohot** [[00:04:33](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=273)]
Uh, yeah. So that's rangeify. There's a chance we'll get it merged this week.

##### **Geohot** [[00:04:39](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=279)]
Uh.. Maybe. I mean, there's a lot of stuff. I gotta put tensor cores back, and I gotta put optimizations back. But I think I have decent ways to do that.

##### **Chenyu** [[00:04:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=290)]
And this kind of rips out.. And you also need a new spec. Do you have a new spec for specifying optimization for multireduce?

##### **Geohot** [[00:04:57](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=297)]
Yeah, so that one, the way that I'm dealing with, is just gonna be, uh.. It's gonna just put all the axes in a list. And, like, right now, if you have multireduce, you say unroll 0, and you have, like, two reduces in parallel. Serial reduces already does this for it, but if you have parallel reduces, that 0 will apply to both. But in the new case, it's just gonna be a different axis.

##### **Geohot** [[00:05:22](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=322)]
It's a pretty simple spec. Cool. Sounds good. Uh.. Yeah, so..

##### **Chenyu** [[00:05:30](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=330)]
Next is LLaMA. I've posted a new picture for what we have. Uh.. So the place I put a date is I can train that thing so that the training loss reduced to, uh, 7, or something like that. So training is training. We have to get to 5.6? Yeah, it's 5.6 for eval loss. Have we hit anything at 5.6? Yes. Oh, really? If you train the 7 once for longer, the training loss hits 5.6, but that goes to the.. my usual question for World's Pirates, that we want to see the correct eval script.

##### **Wozeparrot** [[00:06:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=377)]
Yeah. This week I'll work on eval so that.. Yes.. we can actually have..

##### **Chenyu** [[00:06:22](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=382)]
Because now it's sketchily fast how we hit 5.6. Because we train from, like, random weight, right? We don't.. We are not even from, like, a pre-trained weight. Oh, not totally random weight.

##### **Wozeparrot** [[00:06:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=395)]
The only thing is our LR is very high.

##### **Chenyu** [[00:06:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=397)]
No, but that's.. LR is, uh.. Okay. It's probably not a hyperparameter, but you.. I don't think this benchmark is that bad.

##### **Geohot** [[00:06:49](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=409)]
Well, but we're not.. Okay, we're not starting from random weights. We're starting from random weights. We're starting from weights or we're just changing one layer, right? Uh, for the 1B..

##### **Geohot** [[00:06:57](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=417)]
No, for.. No, no. For the current thing we put, it's front-render, right? Oh. Seems like a bug. Yeah, that's what I mean. Uh, so..

##### **Chenyu** [[00:07:07](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=427)]
So, I post a few things I can think of. It's most likely we might have some issue in our thing, or our training laws and eval laws are very different. We are not actually training, or this benchmark is bad. So, we want to rule out our fault first and decide. It's not like we would change anything, because for MLPerf, we cannot change learning rate for this one. We need to be exactly the same. So..

##### **Geohot** [[00:07:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=457)]
Well, I mean, yeah, let's just get an eval up and check it. I mean, there's lots of things that can do this with training laws. Like, for example, say you're showing the same example over and over again. Yes. That'll get your training laws through really well.

##### **Chenyu** [[00:07:46](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=466)]
Uh, I have even worse hypothesis, but.. Okay. Yeah. Yeah, so let's eval. Uh, but the hello there seems fine. It's good. Yeah, model parallel.. That's.. I put the code in, and for 8B, it seems to be correct. But for 70B on MI300X, I got the compile error from.. com.. GR? Com.. Yeah, from the compiler. So, I will find what's the problem with.. with the kernel. I mean, those kernels are really big, so I'll.. I'll find that and see what the issue is, and see if we need to update the compiler version or anything like that. By model parallel, you mean you're putting a bunch of layers on each? Yeah, just split every layer on the A machine. Yeah.

##### **Wozeparrot** [[00:08:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=517)]
Have you tested if it works with LLVM? Because on MI300, it should work with LLVM, I think.

##### **Chenyu** [[00:08:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=523)]
Oh, sure, I can test that. So I haven't really seen what the error is.

##### **Geohot** [[00:08:49](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=529)]
Okay.

##### **Chenyu** [[00:08:49](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=529)]
So that's what I will do. That.. And that also.. It's either a compile.. No, it's not a compile. So the.. I think scheduling or something around that is also very slow. But I will find a better report before I complain too much. The last one is gradient accumulation memory. So gradient accumulation, I also put the code in. I stare for it for a while, and my expectation is.. If you increase the accumulation numbers, the input to the training function will proportionally be bigger because now we are feeding a bigger batch. But because internally, for every mini-batch, I realize all the gradients, so in my imagination, if we don't have lingering buffer and memory planner works correctly, it should not use more memory between mini-batches. Hence, I let gradients die. But for now, I can see.. Not everything is free, and the memory usage increases if you increase gradient accumulation numbers. You should just be jitting one mini-batch and then.. No, that doesn't work.

##### **Geohot** [[00:10:02](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=602)]
Why? How does that work? Jit one mini-batch.

##### **Sieds Lykles** [[00:10:06](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=606)]
Okay.

##### **Chenyu** [[00:10:08](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=608)]
Then what's your training function?

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=611)]
Do you jit that too? Uh.. On the outside? Yeah. So we need.. We need real-life to happen for forward and backward, right?

##### **Chenyu** [[00:10:26](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=626)]
Okay. So that thing, if you want to jit, you jit together? No, I wouldn't jit it together.

##### **Geohot** [[00:10:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=632)]
So I would just jit one mini-batch forward-backward

##### **Chenyu** [[00:10:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=635)]
and have it store the gradients. No, how do you have backward before in your mini-batch? What? We are doing gradient accumulation. Okay. So what do you mean by backward?

##### **Geohot** [[00:10:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=645)]
Backward. Not optimizer, just backward. Okay.

##### **Geohot** [[00:10:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=650)]
Okay, so you have one.. You have a jit which does a forward and a backward. Okay. That's a mini-batch.

##### **Geohot** [[00:10:56](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=656)]
Okay.

##### **Geohot** [[00:10:57](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=657)]
Then you call that jit however many times you want a gradient to accumulate.

##### **Geohot** [[00:11:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=661)]
Okay.

##### **Geohot** [[00:11:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=661)]
You have to.. You might have to pre-initialize the gradients outside of the jit.

##### **Chenyu** [[00:11:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=665)]
You might have to do like zeroes, contiguous, and all the gradients. Okay. So for every other stuff, it's not jitting?

##### **Geohot** [[00:11:13](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=673)]
What other stuff? Well, then you can jit the optimizer separately. Okay.

##### **Sieds Lykles** [[00:11:18](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=678)]
So you have the jit in the front, the jit in the back, and then..

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=682)]
Then you just have a for loop in Python, which calls that jit in mini-batch a hundred times, or however many times you're calling it. And then you have another jit-ed thing that's the optimizer. Okay. Yeah. Maybe. Oh, yeah, yeah, no. Whoa, whoa, whoa. It's going to take absolutely forever to schedule and stuff if you try to run all the mini-batches

##### **Geohot** [[00:11:38](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=698)]
and put that in one jit. Okay. Maybe. That makes sense. That's just very hard to use. Why? It's just hard to use. It's a bad user experience.

##### **Geohot** [[00:11:56](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=716)]
I think this is hard to use. I mean, you might want a helper function on the optimizer, which actually zeroes the gradients

##### **Geohot** [[00:12:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=723)]
and creates those.. I don't know what you're saying. No, then..

##### **Geohot** [[00:12:13](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=733)]
How do you put the input to the mini-batch?

##### **Chenyu** [[00:12:16](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=736)]
Anyway, there are.. Oh, yeah. There are hard-to-use parts of this.

##### **Geohot** [[00:12:23](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=743)]
Unless I'm missing something, this doesn't seem that hard. It's probably not hard. It's just annoying.

##### **Chenyu** [[00:12:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=751)]
But anyway..

##### **Geohot** [[00:12:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=752)]
Well, I'm not sure what you want it to be. What do you mean? You want to run all the mini-batches inside of a single jit?

##### **Geohot** [[00:12:40](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=760)]
Yeah. Is there a reason that it wouldn't work?

##### **Chenyu** [[00:12:46](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=766)]
Uh.. I don't know. So for now, it's working.

##### **Geohot** [[00:12:49](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=769)]
I mean, it would work. It'll just.. Like, how many mini-batches are we talking? If it's like two, sure, whatever. Who cares? But if it's like 100? It can take forever. For 4 or 5B, I think it's 1,000. It's 1,100 or something. Yeah, exactly. So we're definitely going to put that in an outer Python loop. No.. Okay, anyway. Maybe.. But there's no way you can run 1,100 and ask it to schedule.

##### **Geohot** [[00:13:12](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=792)]
No. They are all the same. Yeah, but it doesn't know that.

##### **Sieds Lykles** [[00:13:16](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=796)]
Yeah, but it doesn't know that. Yeah, but it doesn't know that.

##### **Chenyu** [[00:13:18](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=798)]
Sure, I mean, that's trading capability to user experience. The real thing here is that it shouldn't be any of this. The real thing here is that it should be a range. Yeah, but it's not going to be a range soon, so..

##### **Geohot** [[00:13:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=808)]
Yeah, but it's not going to be a.. Well, but no, I think, yeah, for now, just.. Okay, I was thinking.. I'll write a simple example if I'm missing something about why this is hard. You are going to need one either helper function or a one-line forward loop that actually creates

##### **Geohot** [[00:13:44](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=824)]
the gradients as zeros. Okay. Because otherwise, your first mini batch is different, right? Yeah. Which might even still work with the JIT.

##### **Geohot** [[00:14:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=841)]
And the JIT is pretty good about that. Like the JIT.. No, our JIT is very janky about weird.. No, but it won't capture the first run. It'll only capture the second run. It might just work.

##### **Sieds Lykles** [[00:14:11](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=851)]
Okay, sure.

##### **Chenyu** [[00:14:12](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=852)]
Then you can write an example to your beautiful MNIST or something. Yeah, yeah, yeah, yeah.

##### **Geohot** [[00:14:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=857)]
I mean, I'm not sure if it's going to work or not, but.. You want a gradient accumulation example? Yeah.

##### **Chenyu** [[00:14:19](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=859)]
Okay. But regardless, I'm still interested to know why the current implementation have memory issue, and that's the specific questions I have I post in viz. I think it's nice if our tools can show that.

##### **Geohot** [[00:14:38](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=878)]
Probably because it's not inserting contiguouses. Yeah. I also want to know where.

##### **Chenyu** [[00:14:46](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=886)]
Yeah. In the gradients, right? Like.. If I already realize all the gradients.

##### **Geohot** [[00:14:54](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=894)]
Oh, it's still doing it? Yeah. Oh, okay. That's your note.

##### **Chenyu** [[00:14:57](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=897)]
Okay. Anyway. Yeah. So other stuff I think people can talk when it's their term still wants. The faster MI thing, whether it's the AQL sync or AM driver or.. Whatever. That. We have eval. Then we have.. We want this to work. For now, it's struggling if I have like a few millions of rewrites. And so I think I post the current thing that we have. So for anything 7TB, I should get.. Once I fix the compile issue, we should get the 512 one working. That one fits into memory. For anything with bigger context, we need the rentify or flash attention like stuff to start not creating too many context. Too many buffers with context square. Nice.

##### **Sieds Lykles** [[00:16:04](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=964)]
Yeah.

##### **Chenyu** [[00:16:07](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=967)]
So we'll see where we are. I also follow up with the 8B thing. So they are supposed to merge everything and have a documentation ready. Like last week, but it's not ready yet. So we'll see if we got that this week. Once that is ready, we can.. We should also prepare the data loader for that. And that one, we should really be like training regardless of other optimization.

##### **Geohot** [[00:16:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=991)]
Do we know what the context size is? A192? Oh, wow.

##### **Wozeparrot** [[00:16:36](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=996)]
But it uses the original LLaMA tokenizer. So the vocab size is way larger.

##### **Chenyu** [[00:16:42](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1002)]
Yeah, but we have fused ARANGE or whatever. So.. I don't know. We will see.

##### **Geohot** [[00:16:48](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1008)]
That's crazy that they went from BERT and their replacement for BERT is an 8B with an 8192 context.

##### **Chenyu** [[00:16:55](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1015)]
Yeah, because that's everyone using now. So..

##### **Wozeparrot** [[00:16:59](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1019)]
8192 context? Really?

##### **Geohot** [[00:17:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1021)]
Yeah.

##### **Wozeparrot** [[00:17:02](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1022)]
I mean, 8192 is small now.

##### **Geohot** [[00:17:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1025)]
Yeah.

##### **Chenyu** [[00:17:06](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1026)]
I don't know. Another thing that I'm interested in, maybe we can talk later, is multi-machine. So we previously said.. We want to try the multi-machine on BERT, but BERT is gone. So for 8B, I still want to see like a script or some easy to use thing that I can try like multi-machine BERT, training BERT. But we also.. Because our contract also has a multi-machine part. So for the 8B, we might as well just also run the two machine 8B on it and submit like this one.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1062)]
Yeah. Well, it's pretty.. Have you been following what UVM stuff is? I don't know why a kernel driver got involved. I think it's fine to just use the AMD.

##### **Wozeparrot** [[00:17:52](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1072)]
Yeah. So supposedly the AMD thing had some bug, but I think he thinks it's just scheduling related. I think it hits the.. Well, he says that it hits the target if you just use the AMD driver.

##### **Geohot** [[00:18:04](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1084)]
Yeah. You want to test it and tell me when to pay out that bounty? Yeah.

##### **Geohot** [[00:18:08](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1088)]
I'll test it this week. Okay. Yeah. So..

##### **Chenyu** [[00:18:13](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1093)]
So I want to see some tutorial easy to use or ready to pay for the Cloud Bounty because we also need that for MLPerf. Yep. I think that's everything I have now.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1109)]
And we can move on to this.

##### **Qazalin** [[00:18:34](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1114)]
I have a reapplication of Nimlgen's original PR without all the behavior changes, really. I've been trying to do a lot of this stuff, but I don't know if I can do it in the future. Hopefully we'll merge that soon. Maybe tonight. And clean that up. Basically, it's actually pretty good that it makes this for the CPUs, for the CPUs to follow faster for the timelines of the kernels. Right now in masters open, the, like, for LAMA, it will struggle a lot to zoom correctly. That should be fixed. I'm working on some refactors to make it nicer to look for HTTP runs. I think we optimized a lot for one device, but we should be able to support a lot more use cases.

##### **Geohot** [[00:19:30](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1170)]
So is this perf just for the timeline view, or will it also be for the memory view?

##### **Qazalin** [[00:19:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1177)]
It is just for the timeline view. I think we can genericize it at some point. Any generic shape.

##### **Geohot** [[00:19:48](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1188)]
Cool. I don't want to add, I really didn't like the checkbox. The problem with doing that is now no one's ever going to make this fast because it's behind a checkbox. So it's still going to be slow because of the memory for now.

##### **Qazalin** [[00:20:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1205)]
The checkbox exists, it's just default true.

##### **Geohot** [[00:20:08](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1208)]
Okay. Okay, the checkbox can exist for six days.

##### **Sieds Lykles** [[00:20:20](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1220)]
Okay.

##### **Geohot** [[00:20:21](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1221)]
But yeah, again, is there a fundamental reason why it's harder to make the memory fast or you just need to do it?

##### **Qazalin** [[00:20:27](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1227)]
I don't think so. I think it's..

##### **Nimlgen** [[00:20:30](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1230)]
I mean, it's n squared right now. And I think if we kind of want to draw like the same thing, we can do it. If we draw right now, we can do better. I mean, we can also try to optimize, like not draw all buffers, but what's the reason for the such visualization?

##### **Geohot** [[00:20:51](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1251)]
Yeah, I mean, if it's n squared, we got to just fix that. There's no reason that algorithm has to be n squared. What algorithm? Whatever we're using to draw the memory, like those.. All those things?

##### **Geohot** [[00:21:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1265)]
Yeah, yeah, yeah. I don't even know how it's n squared.

##### **Geohot** [[00:21:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1269)]
Okay.

##### **Geohot** [[00:21:11](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1271)]
Okay, cool. Yeah, but no, it sounds like this stuff could be improved. I mean, you see, like the minute you put something behind a toggle, even if it's default true, it's like.. It's just an excuse to make it not performant. I don't know, we need to.. There's lots of places in TinyGrab where this is bad. Like we need to move away in general from.. Oh, just stick it behind an environment variable. Oh, it works some of the time. Oh, you just have to know. So. But cool. Good to see the performance stuff coming back. Yeah, and then optimizing for the thinking about the 8 GPU case. I wonder if we can have like a.. Do we have like a mock 8 GPU thing? Which will draw a viz for us? Like we have 8 null devices?

##### **Geohot** [[00:21:58](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1318)]
Yeah.

##### **Qazalin** [[00:22:00](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1320)]
Null devices don't have timing. It's just instant.

##### **Geohot** [[00:22:04](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1324)]
You just don't have.. Wait, null devices totally have.. Yeah. It's instant. It's not instant. Nothing's instant.

##### **Qazalin** [[00:22:14](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1334)]
I mean, like, I would have to put sleep in the call.

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1337)]
No, why are you putting sleep in the call? It shouldn't be instant. Nothing is instant on a computer. How many nanoseconds is it?

##### **Geohot** [[00:22:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1348)]
It's not going to be very informative, but okay, yeah.

##### **Qazalin** [[00:22:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1351)]
I mean, I have like a real run on the 8 GPUs.

##### **Geohot** [[00:22:34](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1354)]
No, I mean, I agree that it totally.. Like, it's not like the null device is going to give you any sort of real stuff, but it should at least have some timing information.

##### **Chenyu** [[00:22:48](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1368)]
Yeah, I think it was already working.

##### **Geohot** [[00:22:51](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1371)]
Is it? Let's see.

##### **Qazalin** [[00:22:53](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1373)]
It's not, because null is not an ACQ device, and only ACQ devices are fulfilled.

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1380)]
Ah. Yeah, I don't see any kernels on the null timeline.

##### **Geohot** [[00:23:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1389)]
Yeah, I think, I think, I mean, it's okay if you have to like zoom way in because it's only taking nanoseconds, but it's still going to take time. Null should probably be an ACQ device, yeah.

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1405)]
I mean, everything should be an ACQ device, I think.

##### **Chenyu** [[00:23:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1408)]
Then what's an ACQ device? Is it just not a device?

##### **Geohot** [[00:23:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1411)]
It's just a device, yeah, I think so. I think we've got to get there, get there eventually. But yeah, no, so I'm running, I'm running with.. The null device has memory, but it doesn't have timings, and it should. Okay. Wait, but metal's not an ACQ device, and metal has timings.

##### **Qazalin** [[00:23:53](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1433)]
Hmm, I think NullGen added the profiling for metal and ACQ.

##### **Geohot** [[00:23:59](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1439)]
See. Yeah, now CPUs are ACQ devices, okay, that makes sense. Yeah, I think, I think null is the best way to do it. Yeah, I think Null needs timing, too. And then we can, and then we can like test stuff with, with 8 GPUs pretty nicely.

##### **Chenyu** [[00:24:16](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1456)]
Oh, and a, and a Python marker idea is for.. Because I want to plant a marker somewhere before to debug my great ACC. So that should replace the usage of printing stuff in Python, then read the debug equals to log in between. Do you want a marker, or do you want like a width? No, I want the, I don't, I don't know which one is better.

##### **Geohot** [[00:24:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1483)]
I, I think it'd be cool to have like a, like a, like a width. You could say like width, and then you put your training in a width, and you put your test in a width, and then it shows like training, test. Maybe we should support both, but, I mean, the problem with just a marker is what's the start and stop? Like we don't really have that.

##### **Chenyu** [[00:25:04](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1504)]
No, but I would imagine. I would imagine marker is the primitive you want, and your width is just planting two markers, something like that.

##### **Geohot** [[00:25:11](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1511)]
How is this stuff done now? Do we have like a start and an end, or do we have.. Oh, we don't have this.

##### **Chenyu** [[00:25:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1517)]
I just print.

##### **Geohot** [[00:25:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1517)]
No, no, no, I know, but I'm saying like in general, like how are most things tracked?

##### **Qazalin** [[00:25:22](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1522)]
Most things are how they start and end, yeah. The range.

##### **Geohot** [[00:25:26](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1526)]
And they have the start and the end in a single, like do we have any sort of infrastructure that looks like a marker at a single point?

##### **Geohot** [[00:25:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1537)]
No, I mean, we can just create an event that starts and ends are the same.

##### **Qazalin** [[00:25:40](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1540)]
We do, for the buffer allocation and the allocation, those are point events.

##### **Geohot** [[00:25:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1545)]
Those are point events, okay. And then do we have anything..

##### **Qazalin** [[00:25:48](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1548)]
Like I would imagine, Chen, you wanted horizontal line in the timeline, right? Or sorry, like vertical line on like the entire span of the screen. Yes. Like a red line. With like a two pixel.

##### **Chenyu** [[00:26:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1565)]
So say if my thing somewhere here, I've put events, I want a line like this. Oh, you want a whole big vertical line. So I know at that point what happened on every device. Because for now you see memory use increase, but you don't know like which part of a Python is increasing.

##### **Geohot** [[00:26:29](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1589)]
I see. Yes. Yes.

##### **Chenyu** [[00:26:33](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1593)]
Okay. Yeah.

##### **Geohot** [[00:26:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1595)]
How much effort will this be?

##### **Qazalin** [[00:26:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1597)]
Not a lot. I'll add it.

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1599)]
Cool. Yeah, I like kind of both things. I like kind of the.. I mean, also we should think about how we can track these things back to like the Python. Like especially with this event thing, it'd be cool if it just said, oh, here's the, you know, the file and line number. With like, I don't know if we have like universal infrastructure for like the VS Code links. I've never used it. But okay, cool. So you want like a whole, you want like a whole line. From all the way. A whole vertical line.

##### **Chenyu** [[00:27:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1625)]
Basically a way for me to.. It's like debugger. Like you advance, advance, advance, and you stop somewhere and see, okay, what's the buffer on every..

##### **Geohot** [[00:27:18](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1638)]
Yeah, you're looking at that line and you're seeing what's allocated and stuff. Yeah, cool.

##### **Sieds Lykles** [[00:27:22](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1642)]
Cool. Okay.

##### **Qazalin** [[00:27:25](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1645)]
Okay. You mentioned SQTT too. I did my work on just like the Python. Just decoding it. So right now the status is that it can decode the raw stuff. I have a feeling that they're going to open source the other decoder with closed source. I didn't spend time reverse engineering it. But yeah.

##### **Geohot** [[00:27:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1665)]
I really can ask.

##### **Geohot** [[00:27:49](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1669)]
Just yeah, write up an AMD hardware what you want open source. And I'll forward that to our contacts at AMD. Also, the thing is, I think it's a good idea to have a source code. You can have things where it's like.. Wait, so you're talking about this RockProf trace decoder that's not open source?

##### **Sieds Lykles** [[00:28:07](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1687)]
Yeah.

##### **Geohot** [[00:28:10](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1690)]
Wait, it's.. What?

##### **Geohot** [[00:28:14](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1694)]
It's closed source and they just have an SO file?

##### **Qazalin** [[00:28:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1697)]
Yeah. Yeah. It's absurd. And it doesn't require any raw cam install to run it.

##### **Geohot** [[00:28:23](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1703)]
I see. So this is the thing you want open source. All right, cool. I'll post about it on Twitter.

##### **Geohot** [[00:28:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1708)]
We'll see. Okay.

##### **Qazalin** [[00:28:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1711)]
That's the only thing that's fetching.

##### **Geohot** [[00:28:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1715)]
Yeah. Yeah, I see. So what's the API to this thing? It's just an SO file? It doesn't even have a header?

##### **Qazalin** [[00:28:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1725)]
Nothing. Nothing. I..

##### **Geohot** [[00:28:48](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1728)]
Where's this tool that they're talking about? Oh, it's a plugin library for the RockProfiler SDK, which is retired. We should use the RockM systems repository. Oh.

##### **Sieds Lykles** [[00:28:59](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1739)]
Okay.

##### **Qazalin** [[00:29:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1743)]
But yeah, I mean, it works.

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1747)]
And it's correct. I think.. It's just burn cycles and it looks great. Cool.

##### **Geohot** [[00:29:20](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1760)]
Yeah, and then I see you using.. I see that in the disassembler, you're using Co-Manager. Any reason to use Co-Manager and not LLVM? Oh, I don't know.

##### **Sieds Lykles** [[00:29:27](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1767)]
I don't know if you can see it.

##### **Qazalin** [[00:29:29](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1769)]
I don't know if you can see it. LLVM errors out. Like the LLVM has four different disassembly APIs. I'll try more. I'll try harder. But yeah.

##### **Geohot** [[00:29:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1777)]
I mean, you can also like Co-Manager's open source. You can read whatever it's calling into.

##### **Qazalin** [[00:29:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1783)]
Yeah. I don't know.

##### **Geohot** [[00:29:46](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1786)]
I'll see. Yeah.

##### **Geohot** [[00:29:47](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1787)]
I mean, there's kind of a question here about like, we might want to start thinking about doing our own.

##### **Qazalin** [[00:29:57](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1797)]
Disassembly? Yeah.

##### **Geohot** [[00:29:58](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1798)]
Well, not really a disassembler, but like kind of like something that'll like, because eventually we're going to want assembly output from these things. So we don't want it. We don't want to disassemble. We want something that can like, like a Python representation of each of these things. Ensure one of them is a print and that just happens to be a disassembler. I don't know. No, I don't think we should think about this yet. Yeah. I'll ask AMD if they can open source that. But then like the stuff you're writing, is it? You're also, I see that you have these things that say you're taking from these header files. Is there any reason we're not just using the C types lib on the header files?

##### **Qazalin** [[00:30:47](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1847)]
Raw cam hasn't yet shipped those headers.

##### **Geohot** [[00:30:51](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1851)]
Well that's okay. You can put the headers in extra.

##### **Qazalin** [[00:30:55](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1855)]
Oh, I see. I see. I see. Okay. Yeah.

##### **Geohot** [[00:30:58](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1858)]
Yeah. Yeah. Put the headers in extra and then use C type libs instead of like manually creating these things.

##### **Qazalin** [[00:31:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1863)]
I see. Yeah. Yeah. Yeah.

##### **Geohot** [[00:31:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1865)]
It doesn't matter where they are. I'm okay with sticking headers and extra interest generating from them.

##### **Geohot** [[00:31:10](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1870)]
Okay.

##### **Sieds Lykles** [[00:31:12](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1872)]
Cool.

##### **Geohot** [[00:31:14](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1874)]
Yeah. Top priority is Viz, Viz performance, Viz features. It's kind of where we are.

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1881)]
And then yeah, second priority is getting into the micro scheduling. Yeah. Next transformer. Yeah.

##### **Nimlgen** [[00:31:41](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1901)]
So, yeah, so for the CPU and the LLaMA floating thing. variance. For the CPU and the LLaMA floating thing, I just get my eyes on the profile. So let me just give you a quick bit I can hydro and actually the whole speed is 5 temai, which is spent in just CPU kernels. So they currently overlapped. I mean, the transfers overlapped with the kernels on the GPU, so that looks fine. But yeah, CPU takes a lot. So the next thing is threading.

##### **Geohot** [[00:32:13](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1933)]
Is actual threading on the CPU.

##### **Nimlgen** [[00:32:15](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1935)]
Yeah, I think we should use several threads just to speed up the CPU kernels.

##### **Geohot** [[00:32:22](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1942)]
Yeah, I mean, I think there's no way. I think you're limited to something like 16 gigs a second if you're on a single thread. I wonder what memory throughput you're getting.

##### **Nimlgen** [[00:32:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1951)]
Yeah, it should be around that.

##### **Geohot** [[00:32:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1955)]
Yeah. But yeah, we got tons of thread potential there. How's the AM-MI300 coming?

##### **Nimlgen** [[00:32:48](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1968)]
It's like everything up to GFX is AM-MI300. It's ready in the PHP and the firmware stuff. So yeah, the next thing is GFX. Cool. Yeah.

##### **Geohot** [[00:33:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1983)]
And yeah, then how about the FastSync?

##### **Nimlgen** [[00:33:08](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=1988)]
Yeah, I mean, I actually haven't seen any disassembler, but both of you. Yeah, I can do AQL. I mean, yes, I've said we're going to have some problems with the synchronization because AQL has only one way to synchronize. It's just the atomic decrement while we just use.. Well, yeah, but yeah, we can..

##### **Geohot** [[00:33:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2012)]
AQL has a PM4 backdoor you can use.

##### **Nimlgen** [[00:33:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2015)]
Yeah, yeah, yeah.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2016)]
I think that might be fine.

##### **Nimlgen** [[00:33:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2017)]
Yeah, I hope that's fast, yeah.

##### **Geohot** [[00:33:40](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2020)]
Yeah, I think it'll be fast. I've read the code for it, and it's very short, the AQL backdoor. The problem.. The thing that we can't.. do with PM4 is like the code to launch the kernel and synchronize the kernel is all in this one big AQL method. But yeah, I think for our normal synchronization, like our between GPU synchronization, we could just use a PM4 backdoor and it'll be fast.

##### **Geohot** [[00:34:12](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2052)]
Yeah, and also another thing.. I'm not sure..

##### **Nimlgen** [[00:34:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2057)]
I don't remember any method or any plugin. to get an AQL to execute in direct buffers. And that could cost us a loss on the CPU speed. We can't just execute in direct buffers.

##### **Geohot** [[00:34:34](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2074)]
Yeah.

##### **Nimlgen** [[00:34:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2075)]
And I don't remember any of these.

##### **Geohot** [[00:34:38](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2078)]
Well, I mean, eventually with the CPU speed, I think we have to start like moving these drivers to tinygrad themselves, and then it'll just compile a Clang program to quickly set whatever you want to set.

##### **Geohot** [[00:34:54](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2094)]
So, yeah. I don't know. I don't know if you have any more questions. I think we're almost done with the QA.

##### **Sieds Lykles** [[00:35:02](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2102)]
We're done with the QA. We're done with the QA. Yeah.

##### **Geohot** [[00:35:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2103)]
Yeah. I think we're done with the QA.

##### **Geohot** [[00:35:04](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2104)]
I mean, that's been my dream for the drivers for a while, like to the point that they're.. The drivers were actually written in tinygrad. The MMIO is tensors. And yeah. I think one of the things we'll work through in Hong Kong is.. I think one of the goals for Hong Kong is merging.. Oh, yeah.. the merging device and HCQ device and thinking about like which of these things we can unify

##### **Geohot** [[00:35:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2128)]
into like a smaller set of primitive abstractions. But yeah. Yeah, for now. Yeah, I think..

##### **Nimlgen** [[00:35:39](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2139)]
Actually, yeah, I thought about that. Yeah, I think GPU.. I mean, GPU backend is.. The one is the hardest to adopt for the HCQ.

##### **Geohot** [[00:35:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2150)]
Wait, sorry. Say that again? Figure it out. I mean, the..

##### **Nimlgen** [[00:35:57](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2157)]
I mean, the GPU backend, it doesn't follow the.. Like the rules, which I'm seeking in HCQ right now. But..

##### **Geohot** [[00:36:06](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2166)]
The GPU like OpenCL.

##### **Sieds Lykles** [[00:36:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2169)]
Yeah, yeah.

##### **Nimlgen** [[00:36:10](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2170)]
The GPU backend.

##### **Geohot** [[00:36:12](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2172)]
Yeah, yeah. I mean, OpenCL has this other problem with the sub buffers are annoying.

##### **Geohot** [[00:36:20](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2180)]
I mean, there's a reason no one likes OpenCL. But, uh.. Cool. Yeah, yeah.

##### **Geohot** [[00:36:29](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2189)]
I think, yeah, per for the.. Per for the CPU offloading and getting rid of that. It's like 10.. It's like 10 microseconds, it seems like for kernel synchronization.

##### **Geohot** [[00:36:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2203)]
Yeah, that seems..

##### **Nimlgen** [[00:36:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2205)]
I mean, that seems a lot.

##### **Geohot** [[00:36:47](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2207)]
But..

##### **Geohot** [[00:36:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2210)]
Yeah, I mean, it's a full.. It's a full atomic.. It's a full atomic to memory. It's a lot better than it was, but still, I think we got to go to.. The AQL thing is using like this secret.. There's like a bunch of like secret MMIO on the mechs that synchronize them all. And the quickest way to do this is just use AQL. I mean, then also the advantage to using AQL is we can start.. Like, we can make it a perfect copy of what HIP is doing.

##### **Geohot** [[00:37:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2237)]
And I will continue to prod AMD and tell them AQL is stupid. Yeah, okay. So yeah, going to finish AM, then AQL, I think, is faster to implement and then CPU holding. Cool.

##### **Sieds Lykles** [[00:37:39](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2259)]
Cool.

##### **Geohot** [[00:37:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2263)]
Next is cloud. Or whatever was better one to add.

##### **Wozeparrot** [[00:37:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2270)]
I mean, I've mainly been doing it on the cloud. I'm doing MLPerf stuff. So I guess the only thing for cloud is I'll test out all the multi-machine stuff and see if it's good.

##### **Geohot** [[00:38:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2281)]
Sounds good. Yeah.

##### **Chenyu** [[00:38:04](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2284)]
And just let George know when it's ready to pay the bounty and have the script so that we can reproduce the multi-machine Bertrand, for example.

##### **Sieds Lykles** [[00:38:16](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2296)]
Yep.

##### **Chenyu** [[00:38:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2297)]
Okay. Symbolic or anything from seeds.

##### **Sieds Lykles** [[00:38:23](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2303)]
So, I can hear him.

##### **Geohot** [[00:38:25](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2305)]
A little bit of background noise, but yeah, I can hear.

##### **Sieds Lykles** [[00:38:29](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2309)]
Okay. So I fixed a bug in the Z3 render where it's like if you're doing floating point load, costing that to int and using that in the index, that was giving problems. So that fixed part of the hang that you posted an issue about. I'm going to go ahead and start. Z3 is still hanging somewhere else in the BEAM search. And this time it's not an exception that it's throwing. And it's only hanging if you do parallel equals greater than zero. So, I'm still trying to get to the bottom of that. It's.. Sorry.

##### **Geohot** [[00:39:24](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2364)]
Parallel should be multi-processed. It should be..

##### **Sieds Lykles** [[00:39:27](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2367)]
Yeah. That's also.. Well, I mean..

##### **Geohot** [[00:39:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2372)]
Well, no. I mean, libraries can be not thread safe, but I don't know a library that's not process safe. Maybe it's an initialization issue.

##### **Sieds Lykles** [[00:39:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2385)]
Yeah. I'm not sure.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2390)]
But yeah, no. I saw we have four. We have compEQ now.

##### **Sieds Lykles** [[00:39:54](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2394)]
Yeah. Chrome is looking a lot nicer. Also, like, most of the more than equal to one stuff is gone. Cool. And the David and Walt folding factor is almost done.

##### **Geohot** [[00:40:12](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2412)]
Great. Yeah. I think we always have some subtle bugs in there. Hopefully, they're gone now. Yeah.

##### **Sieds Lykles** [[00:40:20](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2420)]
I tried to move, like, there's a flag. So, there are the correct different vault folding flag. And it's a big one-on-one, I thought, because there's something in OpenPilot that really expects division and modules to be, like, floor division. And if I remove that flag, then it.. Well, it's basically the flag causes division to be rewritten using four diff rules, which is more or less the same if the numerate is negative. But it, like, really needs it for correctness. I thought it was just.. It needed to simplify the gates. But it was actually, like, producing different rules. So, I don't know if it's gonna be the same if I re-simplify it using C, which is a bit weird.

##### **Chenyu** [[00:41:24](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2484)]
So, not entirely sure what that is. But I think the general principle for dealing with OpenPilot is you have enough things on benchmark. And any rewrite you want to test or.. We have a lot of, like, image-related rewrites. So, you can see the rules. It's fine if the kernel number or read image, write image load counts are slightly off. I think as long as the ones that run on benchmark is similar speed, it's okay to change.

##### **Sieds Lykles** [[00:42:02](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2522)]
And it probably goes from, like, 20 gated loads to, like, 120. And when.. I mean, I tried to use, like.. I don't know. I can't.. The simple implications for the gates also become quite tricky because you have to do.. Like, all the simplex we do now is.. You have A plus B. And then it's greater than zero. So, either A or B is greater than zero. But then you can see the case to the How để hogy một kąc is greater than two or greater than three. So, then you have to try like.. like, it re-blows up. So those gates are really hard to simplify with the method we use currently. So I wrote a Z3 gate simplifier, and that also caused incorrectness because of the ZDF thing.

##### **Chenyu** [[00:43:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2589)]
Yeah, so I cannot give you specific suggestions now because I know I don't.. I think there are multiple issues here, but again, I think the general idea is open-padded speed is important, and a lot of simplification rules is pretty much built for that. And we want that to be correct, of course. I think maybe some of it for now is practically correct.

##### **Sieds Lykles** [[00:43:39](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2619)]
The annoying thing is that the incorrect rule is also causing it to be faster. I mean, I think the easiest way to fix it might be.. I mean, I still want to change idiv to be floridiv, and at some point, but then I need to work on the fast idiv. I need that to be complete.

##### **Chenyu** [[00:44:10](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2650)]
Because otherwise it can be a problem. Yeah, I think this is probably better discussed somewhere in the PR order issue. If you need to take a look, just let me know. But the high-level thing, as I said, is we need to keep the open-padded fast, because now they are all like, we could be using the latest block claim for upgrading but aside from that, do the correct thing, do the simplification.

##### **Geohot** [[00:44:46](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2686)]
I have one other symbolic project to think about. You got to get a different mic for next week, too, because you're constantly echoing it on right now.

##### **Sieds Lykles** [[00:45:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2701)]
Okay, sorry.

##### **Geohot** [[00:45:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2703)]
No, you're good. The other project is.. So right now we have logic in reshape, in view to merge reshape. I want to delete view entirely. So we.. Do you know where those tests are, Claire? Where the current symbolic can't do the same things, like reshape window?

##### **Chenyu** [[00:45:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2732)]
Oh, yeah. Oh, yeah. Can I connect? Can I? Yeah.

##### **Geohot** [[00:45:38](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2738)]
Can I connect? I think this is.. We got to upgrade symbolic to pass all these tests. Because rangeify is going to delete view.

##### **Sieds Lykles** [[00:45:48](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2748)]
Yeah. Yeah, I mean, I know a couple of rules that are missing.

##### **Geohot** [[00:45:56](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2756)]
Yeah. Yeah, I mean, you see what I'm talking about, about the reshape, all that logic given view should be symbolic.

##### **Geohot** [[00:46:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2763)]
Yeah. Yeah.

##### **Geohot** [[00:46:08](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2768)]
Then the other thing is that you might run into problems with, is right now we have vmin and vmax. Vmax. And vmin and vmax, it can't simplify if you have something that's basically like define var A minus A. That may not have the right range. You know, this one with.. Like right now, vmin and vmax are recording an int and not a uop. And that might be something that you want to change.

##### **Sieds Lykles** [[00:46:40](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2800)]
Yeah.

##### **Chenyu** [[00:46:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2805)]
But A minus A is something else. It's not about you having different range. But it's like the same thing. So if you have A that's a range from 0 to 5, and you have b that's a range from 0 to 5, then A minus B obviously shouldn't cancel out. Yeah. But A minus A should cancel out? Well, A minus A can cancel out.

##### **Geohot** [[00:47:08](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2828)]
But you can have a bunch of.. All right, you got to.. Your microphone is actually real bad, dude.

##### **Geohot** [[00:47:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2837)]
Okay, anyway. Okay. Yeah.

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2844)]
So sure, if you just have A minus A, that should cancel out. But sometimes you can have like.. Say you have like A plus 3 minus A. I mean..

##### **Chenyu** [[00:47:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2857)]
That's a different problem. That's like an ad group of ad that can cancel each other. Yeah. I mean, yeah. One way to decide.. Changing the vmin and vmax won't solve the case for A plus 3 minus A should be 3. Yeah.

##### **Geohot** [[00:47:54](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2874)]
Why wouldn't changing vmin and vmax solve that? How? It's not a min-max problem.

##### **Chenyu** [[00:48:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2883)]
It's because A should cancel out with A, right? Now you replace A with B with the same min and max. It shouldn't cancel out.

##### **Geohot** [[00:48:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2889)]
Well, yeah, I know. But I'm saying, okay, so like if you have it for.. If you ask it what the max, the min is of A plus B, A plus 3, you can say that the min is A plus 3 and the max is A plus 3, right? Maybe it doesn't work. No. I don't know. I don't know. This is hard to think about. Okay. Anyway. Anyway, we should make sure that we're dealing with all those cases, too. Maybe it's actually just through simplification. We have to look at add chains better and stuff.

##### **Chenyu** [[00:48:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2915)]
Yeah. Okay.

##### **Geohot** [[00:48:39](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2919)]
And change your microphone.

##### **Sieds Lykles** [[00:48:41](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2921)]
Okay.

##### **Geohot** [[00:48:42](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2922)]
Next.

##### **Geohot** [[00:48:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2923)]
On next, I think.. Yeah, we are waiting for.. Oh, yeah. Okay.

##### **Chenyu** [[00:48:56](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2936)]
So, we have a branch for Comma people to test their new OpenPython model with the, like, if op support and cubic support. I just merged the cubic implementation in TinyGrad proper, and we will do the refactor first before we merge the if support, because if support, otherwise, is a little bit hacky, and we don't want that.

##### **Sieds Lykles** [[00:49:21](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2961)]
Okay.

##### **Chenyu** [[00:49:23](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2963)]
And there are segfault issue that seems to be related to metadata.

##### **Geohot** [[00:49:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2968)]
What? Is it metadata? I think it's gotta be like disk, because the ResNet does it, too. And I just looked, and ResNet's not using ONNX.

##### **Geohot** [[00:49:37](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2977)]
Maybe it's a different one. I don't know.

##### **Geohot** [[00:49:39](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2979)]
It seems like the same one. It seems like something broke in disk. I don't know. The segfault's been here for a long time. I can't reproduce it locally. I've tried.

##### **Geohot** [[00:49:55](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=2995)]
Okay. Anyway. I don't know.

##### **Geohot** [[00:50:00](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3000)]
Should I just spend a couple hours on this? Because the segfault existed forever.

##### **Chenyu** [[00:50:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3005)]
Are you sure? If you want to.

##### **B1tg** [[00:50:07](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3007)]
Hey, I have a call for the segment fault.

##### **Geohot** [[00:50:14](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3014)]
Oh, you have an idea what it is?

##### **B1tg** [[00:50:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3017)]
No. I have an issue about this. You know, you can't use it. And it's not seems disk bug.

##### **Geohot** [[00:50:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3028)]
It's not a disk bug, you don't think?

##### **B1tg** [[00:50:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3032)]
Yes. I don't remember clearly. But I can see the segment for the traceback. You can find the issue.

##### **Chenyu** [[00:50:49](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3049)]
Oh, the issue says it might be CPython bug.

##### **Nimlgen** [[00:50:53](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3053)]
I mean, you have some crash dumps, of course, to look into.

##### **B1tg** [[00:51:00](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3060)]
Can you report? There is a link to a gist. I can't report it local. I was reproduced it on this Linux machine to run the script multi times.

##### **Geohot** [[00:51:23](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3083)]
I mean, it sure does look, okay, those do look metadata related. It's in wrapper.

##### **Geohot** [[00:51:31](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3091)]
Everything goes through wrapper?

##### **Geohot** [[00:51:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3092)]
No, I know, but it's in wrapper.

##### **Geohot** [[00:51:40](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3100)]
Okay.

##### **B1tg** [[00:51:42](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3102)]
Untest well. Do you see the traceback?

##### **Geohot** [[00:51:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3110)]
Yeah, I see the traceback. I see them both being in wrapper. Oh, here you got a GDB traceback. Okay, let's say. Yes. P thread bullshit.

##### **Geohot** [[00:52:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3129)]
Metadata set. Okay.

##### **Sieds Lykles** [[00:52:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3137)]
I'm going to go back to the old version. I'm going to go back to the old version.

##### **Geohot** [[00:52:29](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3149)]
Yeah, but that לא

##### **Sieds Lykles** [[00:52:29](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3149)]
Well, so

##### **Geohot** [[00:52:32](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3152)]
Yeah don't know I mean do we have to use this context Sakles thing should be claimed.

##### **B1tg** [[00:52:47](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3167)]
Thank you. If we use this correctly, it could be a Python bug.

##### **Geohot** [[00:52:53](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3173)]
Yeah, I'm just, I mean, one idea to kind of fix this is I see us using this context vars thing that I don't know much about. I think it's the only place we use it. Do we need it? Yeah, I mean, maybe we can just refactor this to use less. I could totally see the internal implementation of this context var thing not being thread safe or something.

##### **Sieds Lykles** [[00:53:30](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3210)]
Okay.

##### **Chenyu** [[00:53:33](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3213)]
Maybe we'll follow up on that. We'll follow up on this in some discussions, right? Yeah, yeah, but cool. It's good to have this. And get this fixed. Yeah, so otherwise I think on access per, like progressing fine. Should be there soon.

##### **Geohot** [[00:53:47](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3227)]
Soon.

##### **Chenyu** [[00:53:52](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3232)]
Okay, other bounties. Oh, I spent some time reading our MOE stuff. I think there are a lot to be gained. One from the sort and the top case specific implementation. So for now, the parts that we select top eight from just 64 values takes a very, very long time and lots of kernels.

##### **Geohot** [[00:54:22](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3262)]
So for me to look at a range of my top K and see what it all is. All right. What's the range of my top key? I'll put top K through range of find see what it fuses. We just, I've seen how many kernels top K is. It's absurd.

##### **Chenyu** [[00:54:36](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3276)]
Yeah, you can try that. Sure. I think I tried to put a fuse somewhere in that block and my machine hand. So.

##### **Geohot** [[00:54:45](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3285)]
Okay. Well, ready for, yeah. You're ready to find my help. Yeah. Okay, great.

##### **Chenyu** [[00:54:50](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3290)]
Yeah. So I think fixing that should be fairly close to the MOE bounty and it should be helpful for anyone who is doing the GPT OSS. But.

##### **Geohot** [[00:55:04](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3304)]
I'll look at top K and range of find and see if the pattern just kind of comes out nice.

##### **Chenyu** [[00:55:10](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3310)]
Yeah. We also use a very clever hack trick to flip flip the comparison order so that it's all the same. What do you mean? So sort go up. Yes. So if you look at this picture, that's your Vitonic sort picture.

##### **Geohot** [[00:55:33](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3333)]
Okay. I don't know what that is.

##### **Chenyu** [[00:55:34](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3334)]
It's basically the order you need to compare stuff and put the bigger one in one direction, a small one, another. Yeah. But you have the blue box and green box. Those are comparing in different directions. Okay. Yeah. So the trick we did in sort is you flip all the green box first. So you only compare one direction. Then you flip it back.

##### **Sieds Lykles** [[00:56:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3361)]
Okay.

##### **Chenyu** [[00:56:02](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3362)]
Yeah.

##### **Geohot** [[00:56:03](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3363)]
So that should mostly be fine. I mean, we have some problems with cat. Like we have some problems in general with. Yeah. So cat is another problem.

##### **Chenyu** [[00:56:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3369)]
Yeah. Cat is more similar to a problem for the slice assigned.

##### **Geohot** [[00:56:19](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3379)]
Yeah. I can. I'll look into. I'll look into these patterns with range of find. Make sure we're getting them. Sure. Yeah. Hopefully this stuff should just be free. Great.

##### **Chenyu** [[00:56:30](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3390)]
Okay. All right. Our bounties. Do we have anything? No.

##### **Wozeparrot** [[00:56:33](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3393)]
Okay.

##### **Geohot** [[00:56:35](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3395)]
Well, the big one is the GBT OSS bounty. Who's going to do that? I don't know. Someone in here.

##### **Chenyu** [[00:56:43](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3403)]
Oh, can we have the WAN 2.2 bounty? WAN? W-A-N? That's the image to video model that's supposed to be very good. I've never heard of this.

##### **Geohot** [[00:56:57](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3417)]
Yeah. How much we offer for it?

##### **Chenyu** [[00:57:00](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3420)]
I don't know how hard it is. It's a model. Also, supposedly should work in like 8GB VRAM or 16GB VRAM.

##### **Geohot** [[00:57:09](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3429)]
Probably like that.

##### **Geohot** [[00:57:13](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3433)]
Mixture of experts. Wow. We really need to just work on our mixture of experts stuff. I don't know. Maybe we should just have it. Just let's get this one first. Okay. Hopefully there's.. I think there's progress on the Thunderbolt thing. That guy's still been posted on Twitter.

##### **Chenyu** [[00:57:28](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3448)]
Oh, I thought he stopped. No. No, he's still working. Okay. So I think he's still working. I think he's still working. Oh, wow. Wolf Parrot, can you find a way to merge Mewon? Okay. Okay.

##### **Geohot** [[00:57:40](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3460)]
Oh, yeah. I think, yeah. I think it's mostly good. Yeah.

##### **Chenyu** [[00:57:42](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3462)]
Yeah. Just do a final style check or any nitpick thing you have. Yep. But otherwise, it should be fine.

##### **Geohot** [[00:57:51](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3471)]
Yeah. I'll just merge it. That's good.

##### **Sieds Lykles** [[00:57:54](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3474)]
Cool.

##### **Geohot** [[00:57:56](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3476)]
Yeah. Anything else? Yeah.

##### **Sieds Lykles** [[00:58:01](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3481)]
I think we're good.

##### **B1tg** [[00:58:05](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3485)]
This is a nice test.

##### **Geohot** [[00:58:15](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3495)]
I'll try to get to that today.

##### **B1tg** [[00:58:18](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3498)]
And I found that after this PR, the multi-tensor test fails, just like the mass transfer test. It looks like a meta theme bug.

##### **Geohot** [[00:58:36](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3516)]
Yeah, but that's only on Metal, right?

##### **B1tg** [[00:58:40](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3520)]
Yeah. I put a sign dev synchronize at the end of the transfer function. This will be fixed. Not sure it's the right fix.

##### **Geohot** [[00:58:59](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3539)]
Yeah, okay. I'll look over the reduce access thing. If that bug's unrelated, then we'll just merge it and disable the test for now.

##### **Geohot** [[00:59:17](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3557)]
Cool. Yep, cool. All reviewed that today.

##### **Chenyu** [[00:59:23](https://www.youtube.com/watch?v=QmGmVAMdxwE&t=3563)]
Great. Okay, I think that's everything. Thank you, everyone. See you next week. Bye.
