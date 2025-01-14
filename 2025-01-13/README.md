# 2025-01-13 Meeting

### Meeting Agenda

**Time:** 9:30 AM San Diego time (PST)
- company update, CES
- dsp contract, python speed, multi
- mlperf bert, multi uneven
- scheduler
- driver
- onnx
- bounties (tensor cores, retinanet, graph rewrite 2.0, int64 idx)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=Ha4yFviaLps)

### Briefing

- CHENYU DID AN INTERVIEW AT CES! Or maybe two interviews, since he made the guy come back for more tinygrad content. Release date no idea.
- We have one TinyBox Pro ready to ship today if you buy it.
- [DSP briefing](#dsp-briefing) explainer for DSP being a wide vector machine
- [AM briefing](#am-project-briefing) targeting USB and CLOUD
- [MLPERF briefing](#mlperf-briefing) doubling bounty payout if submission gets on MLPERF and best way to get hired
- Geohot: "We've got a lot of reds. So also tiny box reds. Great choice. Someone bought one yesterday. I take it back. You made an excellent choice, sir. You have great taste."

### Transcript

**Chenyu** [[00:00:00](https://www.youtube.com/watch?v=Ha4yFviaLps&t=0)]  
Company update.  
I can do CES.  

**Geohot** [[00:00:05](https://www.youtube.com/watch?v=Ha4yFviaLps&t=5)]  
Yeah we went to CES.  
I don't think I've ever gone back to CES.  

**Chenyu** [[00:00:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=12)]  
Oh so on the second day there's a open source person from Red Hat they came  
I gave a very short interview for what Tinygrad is doing and what TinyBox is doing.  

**Geohot** [[00:00:30](https://www.youtube.com/watch?v=Ha4yFviaLps&t=30)]  
And did this help us further company goals?  

**Chenyu** [[00:00:32](https://www.youtube.com/watch?v=Ha4yFviaLps&t=32)]  
I don't know.  
Similar to your streaming, probably.  
I mean, there are definitely people coming and get excited.  
So it's a good life.  
Probably not that useful.  

**Geohot** [[00:00:49](https://www.youtube.com/watch?v=Ha4yFviaLps&t=49)]  
I was happy that Horace mentioned TinyGrad as a modern deep learning framework in his talk about PyTorch and how a lot of people are converging to really what TinyGrad's execution model is.  
This idea of you define the graph lazily, but you never have to deal with the graph.  
Like JAX is the same way.  
MLX is the same way.  
Like he said, like Jax, MLX, and TinyGrad are like examples of modern deep learning frameworks.  
Which like TensorFlow and PyTorch are older.  

**Chenyu** [[00:01:26](https://www.youtube.com/watch?v=Ha4yFviaLps&t=86)]  
Yeah.  
That's great.  
It's always good to have good competition.  

**Geohot** [[00:01:32](https://www.youtube.com/watch?v=Ha4yFviaLps&t=92)]  
Okay.  
We sold a red box.  
We actually already got paid for it.  
Yeah, someone bought a red box, [REDACTED]. *;)*  
No, no, they're great boxes, they're great boxes!  

**Chenyu** [[00:01:40](https://www.youtube.com/watch?v=Ha4yFviaLps&t=102)]  
They are great! What are you talking about.  
This is recorded.  
Please.  

**Geohot** [[00:01:48](https://www.youtube.com/watch?v=Ha4yFviaLps&t=108)]  
I don't know.  
It's very worth $15,000.  
You know, you can save money and you can buy a Redbox.  

**Chenyu** [[00:01:57](https://www.youtube.com/watch?v=Ha4yFviaLps&t=117)]  
You can train ResNet and BERT on it.  

**Geohot** [[00:01:59](https://www.youtube.com/watch?v=Ha4yFviaLps&t=119)]  
Yeah!  
You can run LlaMa on it too.  

**Chenyu** [[00:02:09](https://www.youtube.com/watch?v=Ha4yFviaLps&t=129)]  
Great.  
So CES.  
Yes.  
So there might or might not have an interview sometime in the future.  

**Geohot** [[00:02:13](https://www.youtube.com/watch?v=Ha4yFviaLps&t=133)]  
Oh, like an interview with like Red Hat, like press or?  
No.  
So there's this person that is like semi-professional with their gears and just, he just asked me and...  

**Geohot** [[00:02:26](https://www.youtube.com/watch?v=Ha4yFviaLps&t=146)]  
Oh, oh, you did like an interview.  
Oh, I see.  
Yeah, yeah, yeah.  
Sorry, I didn't follow.  

**Chenyu** [[00:02:31](https://www.youtube.com/watch?v=Ha4yFviaLps&t=151)]  
And that person got more excited.  
So after an hour, he come back again for another short one.  
Like, sure, I don't mind.  
I can talk about TinyGrad for hours if he wants.  

**Geohot** [[00:02:42](https://www.youtube.com/watch?v=Ha4yFviaLps&t=162)]  
Maybe we did get something out of CES.  

**Chenyu** [[00:02:45](https://www.youtube.com/watch?v=Ha4yFviaLps&t=165)]  
Yeah.  
I think it's generally good.  
Okay.  
Next.  
It's yours.  

**Geohot** [[00:02:53](https://www.youtube.com/watch?v=Ha4yFviaLps&t=173)]  
Yeah, so we got maybe I talked about it two meetings ago last week.  
We got a $20,000 contract to port the 845 DSP with a deadline of March 31st.  
So there's several parts to this contract.  
The first part is getting quantization.  
So the target is MobileNet v2, and we need to get TinyGrad running a quantized MobileNet v2 in a way that's amenable to the DSP.  
So basically the math has to be done in, like the multiply needs to be uint8 times, like int8 times int8, and then accumulate in int32.  
And it's going to take some rewrite rules in order to do that.  
You can see that terrible scheduler hack I added.  
And what I found is that a lot of the quantized models on the internet are not very good, but you can quantize them yourself pretty easily with ONNX Runtime.  
So that's good.  
And yeah, we'll get a nice quantized MobileNetv2 running probably this week.  
And then...  

**Chenyu** [[00:03:59](https://www.youtube.com/watch?v=Ha4yFviaLps&t=239)]  
Not very good.  
You are using OnnxRuntime to run this model?  

**Geohot** [[00:04:00](https://www.youtube.com/watch?v=Ha4yFviaLps&t=240)]  
I'm using OnnxRuntime to quantize the model.  
OnnxRuntime has built-in quantization stuff.  

**Chenyu** [[00:04:07](https://www.youtube.com/watch?v=Ha4yFviaLps&t=247)]  
Yeah but is it like a potential TinyGrad bug so it's not good or they are really bad  

**Geohot** [[00:04:11](https://www.youtube.com/watch?v=Ha4yFviaLps&t=251)]  
what do you mean  

**Chenyu** [[00:04:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=252)]  
is it also oh possible that we have a bug somewhere so it's not good right  

**Geohot** [[00:04:18](https://www.youtube.com/watch?v=Ha4yFviaLps&t=258)]  
i don't think so uh no i i think that that like there are some bugs but the bugs do not explain what i think it actually is that they have non-standard input formats  
So if you use the standard ImageNet input preprocessing, it's probably different for their model, and they don't talk about this anywhere.  
So I don't know.  
I also wonder how well Qualcomm posts this.  
How well do they test that?  
Probably not that well.  
So yeah, that's step one.  
And then step two is actually getting the DSP to run fast.  
So it depends how far we want to go with this.  
It depends how smart the compiler is.  
If the compiler is smart, we might just be able to put in the right OptOps, and it might be able to be pretty fast.  
But I kind of think no.  
##### DSP briefing
The DSP is a wide vector machine, which is really not what you want to run ML models, because vector math has arithmetic intensity of 1.  
So arithmetic intensity is how many loads you have to do for a math operation.  
So you load in two vectors.  
They're big vectors.  
They're 1,024-bit vectors, so 128 bytes.  
And then it'll add the two vectors together.  
But you can't have arithmetic intensity of 1.  
That'll never work.  
So arithmetic intensity is defined as the ratio of your math flops to your loads.  
So GPUs deal with this through TensorCores, or you can deal with this through MAC arrays.  
And what these things do is make loads be the square root, because it's a square.  
For the DSP, you have to do shift.  
You can do these shifts in these registers.  
And yeah, I'm not really sure how we're going to express that yet in UOPs and stuff.  
So that's part two.  
Well, I guess part two is hope the compiler can do it, and then part three is do it ourselves.  
Yeah, so that's that.  
I'll be working on that in the background.  
The Python's gotten really slow in TinyGrad, and it's annoying.  
We need to make it faster.  
There's basically two ways to make the Python faster.  
It's either make graph rewrite faster or do less graph rewrite.  
Probably going to be some multi-pronged approach.  
I'm excited to talk about that graph rewrite 2.0 bounty.  
And then for multi, so I actually, the more I look at multi, I realize that I want to do stunning MNIST first.  
Stunning MNIST is simpler to think about because it's sequential.  
So multi and stunning MNIST are basically the same thing.  
But what multi lets you do is it will schedule things in parallel that will be serial in stunning MNIST.  
So it's the idea of putting a range UOP into a shape.  
And what a range UOP and a shape means is run all of these.  
And then how exactly we, whether that range UOP corresponds to time or device is something we can determine later on.  
But you can imagine it's basically the same thing.  

**Chenyu** [[00:07:37](https://www.youtube.com/watch?v=Ha4yFviaLps&t=457)]  
Like it's across time.  
Oh.  

**Geohot** [[00:07:39](https://www.youtube.com/watch?v=Ha4yFviaLps&t=459)]  
Right?  

**Chenyu** [[00:07:40](https://www.youtube.com/watch?v=Ha4yFviaLps&t=460)]  
Fancy.  

**Geohot** [[00:07:42](https://www.youtube.com/watch?v=Ha4yFviaLps&t=462)]  
Right?  
I mean, yeah.  
And if you have like assigns in your graph downstream of the range, you have to do it.  
You have to order those.  
But if you don't have assigns, or the assigns are all independent of each other, if the assigns are independent of each other, you can schedule them together.  
So I think this at least expresses the compute correctly, and then we can think about how to schedule.  
So then, yeah, that's multi.  
I want to delete the current code we have for multi.  
But a lot of this is... I really want the gradient stuff to be in first, because it's annoying to deal with old gradient.  
There's a lot of cleanups blocked on that.  

**Chenyu** [[00:08:29](https://www.youtube.com/watch?v=Ha4yFviaLps&t=509)]  
Okay.  
The next one is about MLPerf BERT.  
Again, we want to make it fast.  
Deadline is late April.  
So I fixed the ring all reduce thing, and now it's better tested.  
The step time is similar to our previous submission.  
Aside from figuring out the way to make Python fast, we also want to see if we can save more memories.  
So George put in the free, some intermediate buffer can be freed.  
There are also the test buffer we generated for beam search and some LRU thingy that needs to manage this memory vector.  
We don't have a counter.  
Counter just means how many we are tracking, but not how many there in LRU.  

**Geohot** [[00:09:31](https://www.youtube.com/watch?v=Ha4yFviaLps&t=571)]  
Oh, yeah, we can separately track in global counters, the LRU cache.  

**Chenyu** [[00:09:33](https://www.youtube.com/watch?v=Ha4yFviaLps&t=573)]  
Yeah, for now, you can just add some size in it.  
So anyway, I'll first figure out a way to, so we either, so we definitely don't want to reset.  
Reset is just not needed if we don't need to.  
But also since this is currently pretty memory bound, the more of a batch we can, bigger batch size we can fit in, the faster it would be.  
Similarly, there are probably after this, the next thing is we're looking to some of the expand in the backwards is pretty bad because we currently realize every expand and maybe some of it's not needed.  
So we'll see.  
We'll see how that goes.  

**Geohot** [[00:10:22](https://www.youtube.com/watch?v=Ha4yFviaLps&t=622)]  
How annoying is your REPL?  
Like how annoying is it to work with this?  

**Chenyu** [[00:10:27](https://www.youtube.com/watch?v=Ha4yFviaLps&t=627)]  
What do you mean?  

**Geohot** [[00:10:28](https://www.youtube.com/watch?v=Ha4yFviaLps&t=628)]  
Like it's slow.  
How annoying does this make it to work with?  

**Chenyu** [[00:10:33](https://www.youtube.com/watch?v=Ha4yFviaLps&t=633)]  
If you are like me, that schedule your time according to how these things work, then it's fine.  

**Geohot** [[00:10:41](https://www.youtube.com/watch?v=Ha4yFviaLps&t=641)]  
Okay, okay.  
I mean, this is just something I'm bad at.  
I mean, this is why the quoting in Twitter infuriated me.  
Like, it's just... I don't know.  
I can't have build times.  

**Chenyu** [[00:10:51](https://www.youtube.com/watch?v=Ha4yFviaLps&t=651)]  
Yeah, so what I do is I will work in parallel, like training this and working on something else at the same time, and maybe that thing can have a faster loop.  
These I think for now, it's about like 30 minutes to see something you change has any effect.  

**Geohot** [[00:11:10](https://www.youtube.com/watch?v=Ha4yFviaLps&t=670)]  
This isn't good.  
This isn't good.  
We got to get that lower.  
I would I would try like, can you write like a unit tests that like, like get get at the core problems of this faster?  

**Chenyu** [[00:11:23](https://www.youtube.com/watch?v=Ha4yFviaLps&t=683)]  
Yeah, the problem now is you don't really know what the core problem is.  
So that 30 minutes is kind of a... So for example, if I'm testing the memory usage, now I can lower the eval frequency, or I can just run more evals and things like that.  
I'm aware of how costly this is.  

**Geohot** [[00:11:42](https://www.youtube.com/watch?v=Ha4yFviaLps&t=702)]  
Yeah, no, I mean, you're probably way better at this than me.  
If you give me a 30-minute REPL, I can't improve anything.  

**Chenyu** [[00:11:47](https://www.youtube.com/watch?v=Ha4yFviaLps&t=707)]  
Okay.  
Yeah, so I think once we figure this out, we'll have ways to make it like a smaller and maybe at length we can assign this as like separate tasks for other people to look into as well.  

**Geohot** [[00:11:59](https://www.youtube.com/watch?v=Ha4yFviaLps&t=719)]  
Yeah, I'm here to help with separate tasks.  
I'm pretty sure that free intermediate thing is right.  
I wrote some tests for it.  

**Chenyu & Geohot** [[00:12:05](https://www.youtube.com/watch?v=Ha4yFviaLps&t=725)]  
Yeah, I just need to use it right because of LRU and other stuff.  
Well, it's not going to free the LRU.  
I mean, you can free the LRU.  
So what I did is I also...  
Free LRU, then I hit other errors.  
That's what I posted.  
No, no, other thing about the driver, not your code.  
Oh, not my code, okay.  
Because you should be able to free intermediates, then free the LRU.  
So I verify that it's free, then those are good.  
So, yes.  
This week, the other thing probably is I will figure out how to do the multi and uneven thing.  
So we want to really not support that thing in general unless we really need to.  
For now, I don't think we have really need to case other than ring all reduce sometimes would give you uneven because ring reduce you need to do like a two-way shard and that might be short on the bad number and that's a number you cannot decide that's for example the size of internal embedding  
Well wait but every gpu should be executing exactly the same thing  
Yeah, so you need to pad in that sense.  
Yeah, we need to make sure.  
So the problem right now with the multistuff is sometime one of the GPUs will execute different kernels from the others.  
There is never an advantage to doing this because either your first kernel is faster or your second kernel is faster and you'll be bound by the slowest.  
So you always want them to execute the same kernel.  
You're like, oh, but the last one is actually only doing a third of the compute.  
Doesn't matter.  
Yeah, but it's not clear if you need to pad it and make it a continuous kernel.  
We'll see.  
We'll see.  
It has to be the same code running on all the GPUs, and we should enforce that.  
Yeah, I'm saying in this case, there might be.  
So if you think about a ring all reduce the residual, there will be a smaller one because you do a 2 way shard.  
And there's no way you control the size of that.  
I'll figure this out.  
But I'm pretty adamant about it, because we want this to scale to 1,000 GPUs.  
So I think the residual in ring-all-reduce is the only case we encounter this.  
So I'll be working on that.  
That's my week.  
And we can move on to scheduler.  

**Qazalin** [[00:14:42](https://www.youtube.com/watch?v=Ha4yFviaLps&t=882)]  
So 8580, I got all the tests to pass, but assign contiguous and image.  
And contiguous specifically, the hack we have for force realize.  
This is constraining the new gradient stuff to merge, but cast before view is completely moved over.  
It's two lines.  
PatternMatcher you can read it, finally.  
So it's basically doing the graph rewrite on the tensors.  
and then doing all the fusion and stuff.  
I think the main constraint is just that we have so many hacks, and it's hard to make progress while those hacks exist.  
This week, I'm just going to try removing those.  
I don't think I can come back at any shape.  
I could start by constraining the way that it's currently written to actually write things correctly.  
So we haven't hacked for assign to do the toposort correctly.  
I'm going to try to see how to do assign.  
Because what assign actually means is that a view of a buffer UOP can mean different things at different parts of the schedule before or after the assign.  
And there has to be a way to tag that view buffer.  
Right now we have preload, but it's not actually a good UOP because it's not local and you can't actually graph rewrite that.  

**Geohot** [[00:16:22](https://www.youtube.com/watch?v=Ha4yFviaLps&t=982)]  
Yeah, so I see what you're saying.  
I mean, it should be such that if you have an assign in your parents, it's the next generation of the buffer.  

**Qazalin** [[00:16:35](https://www.youtube.com/watch?v=Ha4yFviaLps&t=995)]  
Well, your assign becomes a buffer view once you hit the schedule, right?  
Once you hit the AST.  
So the AST itself, the local AST versus the big graph, the local AST itself doesn't have a way to differentiate a view of a buffer between the one that was assigned to and the one that was previously.  
You lose the assigned parent.  

**Geohot** [[00:17:00](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1020)]  
Yeah.  
Yeah, I mean, we might want to... Well, once you're in the local, sure, you'll lose the assigned parent, but we might want to explicitly keep that assigned parent in any downstream buffers, right?  

**Qazalin** [[00:17:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1032)]  
In the downstream buffer source?  

**Geohot** [[00:17:18](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1038)]  
Yeah, in the load, right?  
You can even point, like, the buffer to that assign, right?  
Like, the buffer parent is an assign.  
It's just a way to... I don't know.  
I'm not sure.  
I'm just spitballing here.  
But...  
Yeah, no, we should think through to make sure that, like, the toposort works.  
Like, I think we should move a lot of the scheduler to the way that I'm doing it in linearize.  

**Qazalin** [[00:17:48](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1068)]  
Block, yeah.  

**Geohot** [[00:17:49](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1069)]  
Yeah, and then once we move to block, right, like the beauty of block and the thing that I'm so happy about about the block refactor is that every single, like there's a bunch of things there which make a decision about how to order things.  
I remember you asked me about that.  
Every decision is correct.  
Every decision may not be fast, but it doesn't impact correctness.  
So we need to basically figure out the same thing with assign.  

**Qazalin** [[00:18:15](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1095)]  
What do you do block right now?  

**Geohot** [[00:18:18](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1098)]  
How do I do block right now?  

**Qazalin** [[00:18:20](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1100)]  
Yeah, in the linearize.  
Or something like in assign.  

**Geohot** [[00:18:25](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1105)]  
Oh, you're asking how I make decisions or?  

**Qazalin** [[00:18:28](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1108)]  
How do you group them?  

**Geohot** [[00:18:30](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1110)]  
How do I group them?  
So I group them by first figuring out what there, I have like a key and the key includes ranges they depend on and ifs that they're inside.  
So you could think about the key in that schedule being like kind of like buffers it depends on and even like buffer generations.  
I can look into this a bit if you want.  
I can look into like trying to move the scheduler to block.  
if you think we're there.  
I think that you're right about all these hacks.  
For example, there's instant folding rules in view.  
If I remove those instant folding views, does that impact correctness?  

**Qazalin** [[00:19:27](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1167)]  
This is the interval one miss.  
It only impacts correctness if you have cast before view on.  

**Geohot** [[00:19:37](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1177)]  
yeah this is this is the kind of stuff that's got to be that's got to be fixed  

**Qazalin** [[00:19:42](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1182)]  
yeah that removes it if you can look into the block thing um it's like the assign is blocking that but it's like uh you i read your comment like can this be merged earlier  
yeah i understand each other  

**Geohot** [[00:20:00](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1200)]  
Okay uh yeah okay i can look into this today i can look into trying to rewrite the scheduler with uh  
Well, not the scheduler, but the toposort.  
I can look into replacing the toposort with a block.  

**Qazalin** [[00:20:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1212)]  
If you can remove the need for assigned preloads in schedule item, it just doesn't work.  

**Geohot** [[00:20:18](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1218)]  
First, I have to understand what assigned preloads are, but I can look.  

**Qazalin** [[00:20:23](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1223)]  
It's the hack that I have for it.  

**Geohot** [[00:20:25](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1225)]  
I see.  
I see.  
So otherwise, this is ready to merge.  
And what do you say the other issues were?  

**Qazalin** [[00:20:33](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1233)]  
Image, make things that can't be images, not images.  
You can't graph rewrite things while that thing exists because it breaks the graph rewrite.  
You can have, for example...  

**Geohot** [[00:20:48](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1248)]  
I don't understand.  
I thought that happened at a much lower level.  
I thought that only happened on basically the buffer.  

**Qazalin** [[00:20:57](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1257)]  
That does not happen on the buffer right now.  
That happens...  
Like, exactly when you have a UOP base, like, any UOP base, like, multiply even, even if you don't realize it, that becomes float.  

**Geohot** [[00:21:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1272)]  
Yeah, I don't know.  
Maybe we should just find a way to try to fix that downstream.  
We wasted so much time on that.  
Like, there might be a way to fix that with Atomics.  

**Qazalin** [[00:21:28](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1288)]  
Yeah, actually, like, honestly, I haven't spent time on Image, because, like,  

**Geohot** [[00:21:32](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1292)]  
Yeah.  
Ideally, this shouldn't be a part.  
This shouldn't be dealt with in the scheduler.  
I can think about that, too.  
Take some notes.  

**Qazalin** [[00:21:41](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1301)]  
The scheduler does do the image thing.  

**Geohot** [[00:21:45](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1305)]  
Yeah.  

**Qazalin** [[00:21:46](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1306)]  
It changes the buffer type, and it also changes the type of the AST.  
Like if you have a multiply, load up an image image, and then multiply, the multiply is actually a float, not an image.  
Yeah.  
That's dealt with in the scheduler.  

**Geohot** [[00:22:02](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1322)]  
I'll think if the image thing can be dealt with in a different layer.  

**Qazalin** [[00:22:08](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1328)]  
And yeah, I have a fix for contiguous while contiguous.  
I asked the question in TinyGrad dev if there's a way I can assert that a shape tracker has originated from movement ops on a contiguous size 10, for example.  
I think I can write the spec for contiguous and then merge it.  
That's like deleting force realized completely.  
So basically what I want is like a way to, if I look at the tracker.  

**Geohot** [[00:22:40](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1360)]  
You should never be checking has originated from, right?  
Like has originated from is going to be a source for bugs, right?  
What properties do you want the shape tracker to have independent of where it came from?  

**Qazalin** [[00:22:58](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1378)]  
It's a valid shape tracker on a piece of memory of size 10.  

**Geohot** [[00:23:05](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1385)]  
You want to check the underlying size of the memory?  

**Qazalin** [[00:23:11](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1391)]  
Let's see.  

**Geohot** [[00:23:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1392)]  
Well, no.  
The underlying size of the memory, I put that in the Dtype now.  

**Geohot** [[00:23:15](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1395)]  
You can check that.  

**Qazalin** [[00:23:17](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1397)]  
Oh, the pointer.  

**Geohot** [[00:23:20](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1400)]  
Well, not.  
Yeah, I think it's the pointer.  
Yeah, yeah, yeah.  
The pointer has a size now.  
So that's valid.  
And if you want to know if the shape tracker is valid on that size, you can check real size of the shape tracker and see if it equals the pointer.  
or if it's less than the pointer?  

**Qazalin** [[00:23:38](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1418)]  
Does it work for pads?  

**Geohot** [[00:23:42](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1422)]  
Yeah, it should.  
I mean, if real size doesn't work for pad, that's a bug.  
We should fix it.  

**Qazalin** [[00:23:49](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1429)]  
Yeah, try it again.  
Maybe it's more than my ...  

**Geohot** [[00:23:55](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1435)]  
No, I mean, there may very well be bugs in real size as well.  
I'm not sure how well tested that is.  

**Qazalin** [[00:24:00](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1440)]  
Okay, yeah.  
So I'll get contiguous while contiguous merged, and that should be enough for everything.  
Cool.  

**Geohot** [[00:24:10](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1450)]  
Yeah, okay.  
So you got three blockers, contiguous while contiguous.  
I don't fully understand that, but it sounds like you got that one.  
I'll look into once and for all solving that stupid image problem, even if it involves atomics.  
And I'll look into block schedule as well.  
cool uh you know i'm really excited to have to have gradient unblocked there's a ton of refactors we can do once gradient is in because we can start to do things like you know like the the difference between math trait and simple math trait has to do with function and has to do with what can be having gradients taken of it but like there's no problem anymore uh like you can just put like shift in there you put everything in there so  
I think I'm so happy that we finally have a very clear understanding of what a tensor is and what a UOP is.  
The key difference between a tensor and a UOP is that a UOP is immutable and a tensor can be realized.  
And that's like a fundamental deep difference that's never going to go away.  
And there's nothing less, like it's minimal.  
It's like, you know, proof from the book.  
So, yeah, no, I think the deletion of...  
The most important thing that we should be working on right now is the deletion of gradient, or the merge of that gradient stuff.  
I'm here to help with that.  

**Qazalin** [[00:25:28](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1528)]  
I think once the hacks in the scheduler are gone, the gradient is forcing the scheduler to be more natural.  
It deleted a bunch of stuff and tensor UOP.  
And yeah.  

**Geohot** [[00:25:43](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1543)]  
Yeah, once the stuff's merged, we'll do a great project of understanding the scheduler.  
Great.  
No, it's getting better.  
It's getting better.  
I'm very happy that my don't expand, expand things didn't create any errors.  

**Qazalin** [[00:25:58](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1558)]  
Yeah, I'm looking into the Fusion stuff.  
I don't have a good way to express Fusion.  
The expand thing is a big problem for everyone.  
I think Chenyu also mentioned it.  

**Chenyu** [[00:26:13](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1573)]  
Let's fix the current thing, make it simpler.  
Then we can.  
Fusion is nice.  
We also want that for the back.  
A lot of backward inefficiency is due to that.  
We also want to bring back our variance mean in one kernel thingy.  
Those are exciting follow-ups.  

**Qazalin** [[00:26:36](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1596)]  
The swizzling works right now.  
The graph rewrite style swizzle works.  
You have to write the rule that actually put those in.  

**Chenyu** [[00:26:46](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1606)]  
It's really nice that we can express a lot of these behaviors as rules, and it would just work.  
And the benefit of rules is that you can combine in rules.  
You can group rules.  
You can have rules to express your code and sometimes even search some of it.  
So looking forward to it.  
Cool.  
We can move on to driver.  

**Nimlgen** [[00:27:14](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1634)]  
yeah so did some tweaks previous week uh for am so now we don't leave gpu enable like we disable all the main blocks like is the main gfx uh and we also do not reload forward so some optimizations to launch am faster um yeah so this week  
so um this week i'm going to look into the slowness of copy from disk i think the main reason is because we don't use huge pages uh when we use dma from like when we map cpu pages and yeah because of that i think it's just really bad in effect of performance and um so yeah and also  
I think need to think of two people accessing the same GPU because in some cases and in some timings that might broke the GPU.  
So yeah, especially if just you're loading.  
So yeah, basically there is like one period of time when you just reset your GPU and you have source like on the GPU running.  
And since that time until the SMU is loaded,  
So yeah, just stopping this can leave the GPU in a bad state, yeah.  

**Geohot** [[00:28:52](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1732)]  
There's no point with just a system-wide mutex for that.  
It doesn't have to work.  
It just has to not crash.  
The first process has to work.  
The second process could be unable to acquire a lock, or it could delay until it can get the lock, or whatever.  

**Nimlgen** [[00:29:08](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1748)]  
Yeah, yeah.  
Yeah, and I'm going back to... Oh, I also have mockam to merge.  
So yeah, it's taking a bit longer because of this... Because of the memory, and actually it's just... I mean, actually, yeah, it just takes... I just want all these layers, I mean, memory layer to be fully emulated, I mean, in terms of tail being translations.  
So yeah, it just... But...  
Yeah, it's going to be merged this week.  

**Geohot** [[00:29:47](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1787)]  
Cool.  
Did you just do the set capping for Python?  

**Nimlgen** [[00:29:50](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1790)]  
Yeah.  

**Geohot** [[00:29:52](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1792)]  
Sorry for saying that.  
That's fine.  
It's fine.  
We should not be messing with IOMMUs.  
I hate IOMMUs.  
I think it's just beautiful to have a big 64-bit  
global address space that's everything.  
You say disk is slow because it's not using huge pages?  
Doesn't really make sense to me.  
I mean...  

**Nimlgen** [[00:30:24](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1824)]  
Yeah, I believe... I've seen bad performance, actually.  
I mean, it's still be on the GPU, I think.  
So yeah, because on the GPU, we just map as a lot of 4 kilobyte pages.  
And I think the TLB is quite... So it's not really huge for 4 kilobyte pages, actually, because it just... The TLB is split into several parts, like for huge pages and for small pages.  

**Geohot** [[00:31:01](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1861)]  
You're saying the GPU's TLB is so bad that it can't get the full PCIe bandwidth when you're DMAing from the system?  
At 4K pages?  
That would surprise me.  

**Nimlgen** [[00:31:18](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1878)]  
Yeah, maybe not.  
I don't know.  
It's just really slow.  

**Geohot** [[00:31:25](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1885)]  
Yeah, so we need to separate a few things about disk.  
One of the things that I've always seen be like, um, like allocating new memory on the CPU in the Linux kernel is absurdly slow.  
But it should never be doing that you should have like a pre allocated buffer, I think what you want to do is separate the disk thing into two parts.  
There's one part where you're DMAing from host memory, pinned host memory, like host memory that has a fixed physical address to the GPU.  
And then you're DMAing from the disk to the physical memory.  
And then you can double buffer that.  
But you can benchmark each one of those things individually.  
And it would absolutely shock me if the GPU's TLB was so bad that it couldn't sustain PCIe bandwidth.  

**Nimlgen** [[00:32:09](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1929)]  
So actually, yeah, we do this way.  
But...  
Yeah, AMD is fast, AM is slow.  
But it's only when it comes to system pages.  
And I think the bandwidth between GPUs on AM is the same as AMD.  
So it's only something with CPU communication.  
But OK, I'll just have a look at that.  
So I think it's just something stupid I'm missing there.  

**Geohot** [[00:32:46](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1966)]  
And then when I run with debug equals two, does it show me about like 10 lines, like which firmware it's loading and like three lines if it's a hot load or something?  

**Nimlgen** [[00:32:54](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1974)]  
Yeah, it should already do that.  

**Geohot** [[00:32:57](https://www.youtube.com/watch?v=Ha4yFviaLps&t=1977)]  
Great.  
The other thing that I'm kind of concerned about.  
So the AMD driver has a lot of power management stuff.  
And right now I believe that with AM, Rock MSMI is not going to work, so we're not going to be able to see the power.  
Can we query the power of the GPU and see that when you put the GPU in an idle state, how much power it's drawing?  

**Nimlgen** [[00:33:23](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2003)]  
Oh, yeah.  
So yeah, basically all this information is taken from the ECMU.  
Yeah, we can do that definitely.  

**Geohot** [[00:33:32](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2012)]  
Cool.  
And you trust it to, like, we haven't disabled anything.  
Because, I mean, the really, really bad thing would be if we over-temp these things and we disabled some, like, temperature safety thing.  

**Nimlgen** [[00:33:49](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2029)]  
Yeah.  
Like, we haven't thermal alert enabled right now.  
But I think we have interrupts right now and we can just enable this.  

**Geohot** [[00:33:59](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2039)]  
Yeah, we should just be basically monitoring the thermals and the power to make sure we're not doing anything bad.  

**Nimlgen** [[00:34:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2052)]  
OK, yeah.  

**Geohot** [[00:34:14](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2054)]  
But no, cool.  
I mean, it's been great progress.  
##### AM project briefing
Just to talk a little bit about where this is going, I think the AM project is going to two places.  
There's the USB.  
which is going to bring commas inference compute on par with Tesla's.  
We went through this weekend about how many orders of magnitude commas behind in different places.  
And we're two orders of magnitude behind in inference compute now, but if we stick a 7900 XTX in the car, that's as good as Tesla's processor.  
So yeah, there's the USB side of things, and then there's kind of the cloud side of things.  
So we're building right now, we got a shelf in, I'll post some pictures once it's up, but we're building a nine tiny box red test cloud.  
We're going to have two tiny box pros as like ingestion machines.  
I posted a picture of the switch on Twitter.  
So yeah, we should really be thinking about these GPU computers as like the dumbest nodes you could imagine.  
They're just going to sit there, they're going to run some  
Tiny Linux distribution, and then they're going to run TinyGrad.  
It's going to live boot this Linux distribution over Pixie, so it doesn't even have any state on the computer.  
Loads in TinyGrad, loads the AM driver in, and then you can submit basically UOPGraphs.  
Or maybe it even is lower than UOPGraphs.  
Maybe you even submit kernels.  
We can decide where we want to split the boundary.  
It doesn't really matter.  
It's all in the trusted cloud.  
And then, yeah, so we want operations that look like DMA from this address on disk to this GPU.  
And then DMA from this address on disk on node 3 out the network card into node 4 into node 4's GPU.  
And all that should be kind of at PCIe bandwidth.  
So yeah, that's kind of where this is going.  
I think there's been great progress.  

**Chenyu** [[00:36:11](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2171)]  
We still have nine?  
Or just eight now?  

**Geohot** [[00:36:13](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2173)]  
No, we have nine.  
We have extras.  
Oh, we have a lot of TinyBox Reds.  
Is anyone interested in TinyBox Reds?  
They're great computers.  
Take back what I said.  
Cool.  

**Chenyu** [[00:36:23](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2183)]  
Cool.  
Sounds like good progress.  
ONNX, do you get everything you need for ONNX?  

**Geohot** [[00:36:32](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2192)]  
Yeah, you know, it's good that things are fixed, but a little nitpick picks about the... Style.  
Yeah, about the style.  
I mean, I think we want to be moving ONNX more towards high-quality TinyGrad code and not the same quality.  
But now it's like, maybe it's a little bit better than the tests.  
But yeah, I think we really need to think about what's the minimal line count way to express a lot of these ONNX ops.  
And by minimal line count, whenever I talk about minimal line count in TinyGrad,  
I never mean code golf.  
I always mean, well, OK, so this quantization thing is actually being done in these three functions.  
So we can abstract that into a function.  
Here's the right place to draw that boundary.  
It's all about how to correctly factorize  
this whole big problem into pieces such that the sum of the pieces, if you're familiar with the concept of factor graphs, that's kind of how I think about all this stuff, right?  
You can think about Boolean expressions as these massive things, but if you can take out sub-expressions and put them together with ands and ors, you can make simplified Boolean expressions where the sum's totally less, but...  
you're basically describing a good refactor.  
Yes, I'm describing a good refactor, but this is what I mean about the line count.  
I never... This is good for everyone here.  
TinyGrad cares about line count.  
I don't care if you put... Some of it's stylistic, and I just kind of like the style where the four loop has the thing on the same line.  
That's just a personal preference.  
But I never want to see seven clauses shoved into a 150-character line.  
That's unreadable.  
Multiple nested fors and...  

**Chenyu** [[00:38:14](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2294)]  
I think we're pretty on board on this.  
And everyone who contributed to maintaining it has some understanding.  
OK.  
Other bounties.  
TensorCores.  

**Ignaciosica** [[00:38:31](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2311)]  
Hi.  
Hello.  
For TensorFlow for float precision, I need to address accuracy before adding them.  
I don't want to eyeball tolerance or increase until it stops failing.  
I saw a comment from you, ChenYu, on this.  
I want to develop a framework to work over accuracy in tests.  
And this will also span across bfloat16.  
And for Turing...  

**Chenyu** [[00:39:00](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2340)]  
What did I comment?  

**Ignaciosica** [[00:39:08](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2348)]  
That to work on precision for alternative loads instead of to understand them better.  
I don't know if it was or in a pull request, but you said that it was.  

**Chenyu** [[00:39:28](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2368)]  
Yeah, I mean, this is not just for Tensor Core, but we have a lot of one-off, like Float16, some ALUs has different arrows in certain stuff.  
Some of it is under-addressing the issue.  
Some of it is too much.  
But I think Tensor Core is a small enough unit that maybe we can start to do this better.  
So we can say, OK, for  
So we know if you have more adds, potentially you will be noisier.  
And if it is smaller, it's less so.  
So different Dtype definitely depends on your Dtype and your ACC (accumulate) type.  
It also impacts.  
I think this is a good start to not just shove until it passes and try to understand it better.  

**Ignaciosica** [[00:40:18](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2418)]  
Yes.  
Yes, for sure.  
I was thinking in a framework to encapsulate all that in test, not only for Turing support.  

**Chenyu** [[00:40:28](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2428)]  
Maybe just search online to see what other people have to say with this issue.  

**Geohot** [[00:40:36](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2436)]  
How much of this stuff do we have merged?  
How's Turing TC support going, TF32 support?  

**Ignaciosica** [[00:40:44](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2444)]  
No, I have them working in PR, so in my own repo.  
And they work.  
And Turing, I was going to address it in a bit.  
For tensor float 32, the tests that are failing are because of accuracy that I didn't want to eyeball.  
So that's what I left them aside.  

**Chenyu** [[00:41:05](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2465)]  
I think project-wise, it's probably fine if you are fairly sure that's correct so we can support it.  
And I think these like error accuracy analysis can be separate.  
Because we currently don't do that for, I also want this to be done at like float16, right?  
And we are going to support FP8 sometime in the future.  
So I think these can maybe be done like more holistically at that level.  
And TF32 really is just supporting TF32 and your previous refactor already addressed a lot of the issue.  
So I don't think that blocks this one.  
Yeah, I think there's a lot of value in getting this stuff, in getting this stuff merged, get this stuff merged, get paid for the bounty.  
You can come up with a new bounty or something for extra work.  

**Geohot & Chenyu** [[00:41:51](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2511)]  
Yeah, exactly, right?  
The TF32 Tensor Core support, I think it's beyond the scope to have a holistic... If you write some holistic accuracy checking thing, that's like a $1,000 bounty.  
That's very valuable on other levels, if we can start intelligently talking about the fact that floating point math is awful.  
Because that also guides us to know, OK, so now everything we do, acc_dtype, we do in float32.  
Is that good enough?  
Can we do less?  
Or less in what way?  
I think that also links to that part.  
I mean, I think also, yeah, we can have the TF32 thing maybe not be on by default.  
I'm not sure what PyTorch does.  
Is it default or no?  
I don't know.  
So that's part of the analysis for what other people are doing with their tensor cores and what we want to do with our tensor cores.  
Copy, copy, copy.  
No, so I encourage you to clean that up, making sure it's correct, in the sense that it should.  
It's probably fine if it's off a little bit, but it shouldn't be too crazy of an error, something like that.  
Yeah, I think that's right.  

**Ignaciosica** [[00:43:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2592)]  
No, for some tests in CI, it's a little too off for Tensor Float.  

**Geohot** [[00:43:19](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2599)]  
What do you want to fix the bug?  
Yeah, and then I think also, yeah, this is what I mean about you can put it behind a flag if you want, right?  

**Ignaciosica** [[00:43:26](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2606)]  
You can put it behind... I don't think they're very comfortable in increasing that much tolerance.  

**Geohot & Chenyu** [[00:43:34](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2614)]  
Yeah, no, I wouldn't increase the tolerance for all the tests, but maybe create a context var to match whatever PyTorch's context var is, and then just have it...  
You know what I got?  
I think it's fine.  
I'm thinking of a name of that.  
I think it's probably something like precision accumulation.  
Oh, no, no, no, no.  
These are the stupid names.  
There's a torch flag for it.  
This flag controls whether PyTorch is allowed to use Tensor Float 32.  
Oh.  
allow_TF32.  
Great.  
Love it.  
Allow underscore TF32.  
Okay.  
So yeah, you could totally just use that, and then make sure with that flag, there's a bunch of correctness tests that are happening, as in there's not bugs.  
And then precision is something we can deal with later.  

**Ignaciosica** [[00:44:23](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2663)]  
OK.  
And for the Turing Tensor Cores, I mean, the PR is ready.  
I'm writing a guide to reason over Python's emulation to add it to the pull request, and I'm going to send the PR upstream.  
As I said, I'm also going to formalize this guide and the Tensor Cores course guide in order to add them to the docs.  
And as I kind of mentioned on Friday, I guess, I'm going to see if there's a simple way of enforcing Tensor Course shape in order to add them to search.  
And if this works out, there may be value in adding a lot more Tensor Cores shapes.  
Before, I planned on only adding the largest for each Dtype.  
But if there is a space for search over the shapes, I think there are lots of more available shapes worth adding.  

**Geohot & Chenyu** [[00:45:20](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2720)]  
Yeah, so I propose let's get TF32 Tensor Core.  
And if Turing is ready, get it to merge first.  
Then we can talk about, I think the precision analysis is good.  
And also supporting all available Tensor Core is good.  
And we can discuss.  
can set up a bounty or like define like the scope of these so that we incrementally make improvements to tensor cores  
yeah no i think yeah turing tc has is completely separate from the search and you know i shouldn't have i shouldn't have mixed these two together like let's get it merged let's check correctness uh and then i think the new bounty that would make sense is something like if you can get like 150 plus tflops map mall on 4090.  
uh i saw you got it up from like 135 to like 145.  
Maybe with one of these types, it can hit 150.  
And that's the search bounty.  

**Chenyu** [[00:46:15](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2775)]  
Cool.  
OK.  
Cool.  
Good progress.  
OK.  
RetinaNet?  

**Flata** [[00:46:27](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2787)]  
Hi.  
So for the progress, yes, I'll put that hotfix up later today.  
So thanks, Chenyu, for approving that for just the open images data set, just because it was taking a long time and didn't even finish with setting it up on a new machine on the tiny10.  
So that's all good now.  
Now my main task now is to actually just focus on wrapping up the training script and then also including the validation script as well into the training loop so that we can evaluate after every epoch and then I'll start the training run.  
No time estimates yet, but that's kind of like where I'm at right now.  

**Chenyu** [[00:47:05](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2825)]  
Sounds good.  
Cool.  

**Geohot & Chenyu** [[00:47:09](https://www.youtube.com/watch?v=Ha4yFviaLps&t=2829)]  
##### MLPERF briefing
When is the MLPERF, by the way?  
May.  
Early May, so we should, if anything we want to, assuming we do training, not inference.  
Oh, okay.  
Yeah, so because we need to leave like a few days to run the final submission, I would say everything we want to get into the next one, we target late April.  
Cool.  
So if it's ready by late April, we submit.  
If it's not, it's not.  
Yeah, I'm hoping maybe we can have a 5090 machine by then too.  
Great.  
If we have a 5090 machine, we can submit this 5090 machine.  
That would be cool, but there would be a preview.  
It's not available.  
It's in different categories.  
Yes.  
Would not 5090s be available by then?  
Available is defined as the time you submit it.  
You can click buy and buy the machine.  
Oh.  
Yeah, probably.  
I don't know.  
We'll see.  
It's fine.  
Small details.  
Yeah.  
That sounds good.  
Yeah, I think these are a usual thing.  
Just the criteria of done is you can provide me a set of things, instructions, then I can go wrong and finish everything in 24 hours, including your data pre-processing and stuff.  
Yeah, and then I think also the bounty, it's not really expressed here, but if it actually gets on MLPerf, I'll give you double the bounty.  
So if we actually get this on the next MLPerf, it's 1200.  
Yeah, so usually what happens to BERT is you just need to add the MLPerf logging thing and checking with the script.  
It's a, it's relatively simple.  
And of course the time cannot be too bad because these needs to run for, we need like five, 10 rounds for depends on the task.  
So it cannot, it really cannot be like 24 hours to train the model.  
Yeah.  
And the eval also needs to work according to the rules.  
So, yeah.  
But yeah, if we actually get it on MLPerf, it's, you know, it's quite valuable to company.  
Cool.  
And other MLPerf bounties, StableDiffusion, Lama70B LORA, if you can do.  
Great.  
We're very excited.  
Those ones are bigger.  
Those ones are $2,000 if we get them on MLPerf.  
And that's, you know, succeed at one of those if you want a job here.  
Yeah, no, I mean, the StableDiffusion one would be awesome.  
We're also, it's not going to be May.  
It's going to be the... November.  
November, we're going to hopefully have our first cloud submission.  
Yeah.  
54 GPUs all working together to train one of these models in stunning MNIST style.  
Yeah.  
We've got to convert MLPerf to stunning MNIST style.  
We'll see how that goes.  
It's going to happen this year.  
By the end of next year, we're going to be like, wow, you can really just submit this.  
By the end of the year.  
Looking forward to it.  

**Chenyu** [[00:50:22](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3022)]  
Graph, rewrite 2.0.  
OK, here.  

**Tomsa** [[00:50:35](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3035)]  
Hello?  
Can you hear me?  
OK, so I didn't work on the bounty much this last week.  
But I tried to get an upper bound on the speed.  
And I'm pretty sure we can get a 2x speedup.  
I'm not sure about a 4x speedup with a bottom-up automata.  
And also...  

**Geohot** [[00:51:00](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3100)]  
I'll double the bounty for the 2x speedup.  
A thousand bucks for the 2x speedup.  
If you get this stuff merged and it's clean and it's short.  
What I like is how short your PR is.  

**Tomsa** [[00:51:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3072)]  
So one thing about the... Because I'm sort of...  
And I'm not sure if I should do a bottom-up automata or a top-down.  
And there's a couple of reasons, which is if it's a bottom-up, it only applies to the graph rewrite.  
So every time you want to just rewrite a UOP, so for example, for the renderer, you couldn't use a bottom-up rewrite.  
And if you do a top-down, there's one, I guess, cool trick, which is every time you have a variable, that's actually a useless check.  
For example, if you have an add,  
We have two upat.vars that just assign a name, don't have a dtype associated.  
Then currently, we have three checks.  
That's really just one check because the sources will always check, will always pass because they're just nones, basically.  
So you could cut down on a lot of the complexity of the patterns if you do top down.  
But I don't know.  
I'm still deciding on that, I guess.  

**Geohot** [[00:52:09](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3129)]  
Well, I'm not sure exactly why the distinction is top-down or bottom-up.  
But yeah, totally.  
So the name thing is something that can totally be dealt with at compile time.  
So the names mean two different things.  
Some of the names are just literally defining, I want this one returned, which is something that has nothing to do with the match at all.  
So we could pre-compute all the matches.  
I mean, I want to keep the basic idea the same of you have a match function and a rewrite function.  
But match function does not have to loop through all the things.  
Like we have that thing which does the early rejection and like there should be a match function that just returns, oh, here's the list or here's an iterator.  
So, yeah, the names mean two different things.  
The names mean, first off, return this one, which is, again, something that can be dealt with totally after the match.  
Or, if you have two things that have the same name, it's a constraint that they have to be the same UOP.  
But that should just be expressed as a constraint, not as a name.  

**Tomsa** [[00:53:14](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3194)]  
Apparently, I deal with names after the match.  
So, it does happen that the two different uops get assigned different names, then it just fills the match.  
But I think I mentioned the names are separate to the states.  
They're not tied really currently, although you could maybe add them.  
But yeah.  
And there's also a couple of stuff I need to do.  
The current implementation is not.  
Currently, it's actually much slower than the old implementation, but it's because it's not really correctly done.  
What you want is a table for each symbol, a symbol being a unique combination of op, dtype, and arg.  
So you want to first check that the symbol exists and then check, you essentially want to do a product of the sources and then get all the available new states basically.  
Another thing I need to do is it's called a subsumption.  
So if a pattern subsumes another pattern, it means that if the other pattern matches, it itself also matches.  
So it's included in the other pattern.  
And dealing with those means that we don't need to sort the functions at runtime because we've already, essentially, if you have a pattern that's included in another, that function will be included in the other final state so that you can just sort all the functions  
when you're actually building the automaton.  
And then you don't need to sort it at runtime.  
But all those optimizations were already accounted for.  
And that's, with all those optimizations, that's my estimation of like maybe 4x speed, like at most basically.  

**Geohot** [[00:54:43](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3283)]  
Okay, 4x speed, that's two grand.  
So yeah, no, I upped the 2x speed thing.  
It's not like I looked for simple gains.  
It's not simple gains.  
So yeah, you know, a thousand bucks for each 2x we can get.  
And fundamentally, that's the thing that I care about.  
I care about how fast it is and how simple the code is.  

**Tomsa** [[00:55:02](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3302)]  
There's, I guess, a couple of worries, too, of state explosion.  
And I guess we'll have to look at that.  

**Geohot & Chenyu** [[00:55:10](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3310)]  
Yeah, a lot of these checking combinations thing  
You, we can adapt based on the real kernel.  
We were thinking you don't need, you don't really need to overthink for like, what if the rules has like 10 variables or like 10 names to it?  
It's just literally just not happening.  
Make it fast and simple.  
That's all I care about.  
I don't care about like some, some like, yeah, well, sorry.  
Make it correct, fast and simple.  
But yeah, if there's something with 10 variables and that one slows down, I don't care.  
It's not real.  
Cool.  

**Tomsa** [[00:55:46](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3346)]  
I mean, the variable thing is pretty impactful because it happens so often.  
So if you look at the symbolic, the amount of variables that are used that essentially are just checks that always pass is huge, right?  

**Geohot** [[00:55:58](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3358)]  
Yeah, yeah.  
I think that's a good place to get 2x right there.  

**Tomsa** [[00:56:04](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3364)]  
I'll see if I can work more on it this week.  

**Chenyu** [[00:56:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3372)]  
Cool.  
Sounds good.  
uh so int64 index i will probably review it later today i don't know i have a mixed feeling about the pr every time i look at it there's something weird pop out and i need to come in asking why there's that weird thing that wait another day is it  


**Alveoli** [[00:56:31](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3391)]  
Uh hello hello oh yeah um i updated the pr for the the weird thing.  
The Dtype...  

**Chenyu** [[00:56:42](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3402)]  
Is that still the same, that you have a function that has an input called is int64 supported?  

**Alveoli** [[00:56:51](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3411)]  
So I have to get the support from the renderer instance.  
So I ended up putting that in the upcast function, because that's being called by the lower, which has access to the renderer itself.  
and I can just check if it's supported.  
But putting it elsewhere seemed to always require me to check for some additional Dtype.  

**Geohot** [[00:57:17](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3437)]  
Wait, wait, wait, wait, wait.  
If it's not supported, it can just fail.  
We never need to check this, right?  
Because either the thing doesn't require int64, and that's great, or the thing does require int64, it generates a kernel, it tries to render it, and it fails.  
But there's no advantage to it failing in the other way, right?  
So I think I would just assume that it definitely supports int64.  
And if the kernel requires int64 and the device doesn't support it, then OK, it fails.  
But I'd rather it fail with an assert than fail silently with the math being wrong.  

**Alveoli** [[00:57:53](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3473)]  
So it currently fails with the renderer, because when it checks for the mapping between a Dtype and a device-specific Dtype string, it would raise a  
value error because I couldn't find for the WebGPU.  
That's how it fails right now.  
And my PR is you make a fail earlier when the function decides to upcast the UOP.  

**Geohot** [[00:58:21](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3501)]  
I'm fine with it failing the renderer.  
That's fine.  
Again, the current behavior, like right now in TinyGrad, is that it's just silently outputting the wrong math, which is the worst failure.  
Or it crashes.  

**Alveoli** [[00:58:37](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3517)]  
So the upcast will resolve that.  
Oh, the upcasting will resolve that.  
So it just fails on the render now.  

**Geohot** [[00:58:48](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3528)]  
Yeah, failing on the render is fine.  
Let's keep it simple.  
But yeah, again, any failure anywhere in TinyGrad is so much better than a crash or a silent wrong math.  

**Alveoli** [[00:59:01](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3541)]  
Got it.  
I'll just update the PR for that part then.  
But the rest, I think, is all in a good place, and then the testing, it's not dependent on the kernel.py anymore.  

**Chenyu** [[00:59:13](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3553)]  
Oh, OK.  
That's nice.  

**Alveoli** [[00:59:14](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3554)]  
And as a result, the process replay also passed.  
Oh, I have some concern on the process replay, because right now it doesn't fail, because the new added test is not asserting on the render kernel, which is going to be different in the future.  
Like, right now it renders the int64 version,  
If I am not using kernel.py, then process replay won't run.  
Then in the future, if another PR tries to revert that, it wouldn't get caught.  

**Chenyu & Geohot** [[00:59:51](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3591)]  
So you just construct the scene and test the range of?  
Yeah, I think that's OK.  
That's OK.  
That is not in the kernel, and it won't be in process replay.  
Or we have just an explicit test to make sure it's correct and the range is correct.  
So I think that's good.  

**Alveoli** [[01:00:06](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3606)]  
Oh, OK.  

**Chenyu** [[01:00:12](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3612)]  
Yeah, I think it overall looks fine.  
It's just the previous iterations always had something weird.  
OK, so you update this.  
I will take a look later today.  
Okay, that's fine.  

**Geohot** [[01:00:29](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3629)]  
Yeah, that's the meeting.  
We have a TinyBox Pro.  
We have one TinyBox Pro ready to ship today if you buy it.  
So, you know, it's really an incredible computer.  
I talk about 5090s.  
The 5090 is going to cost more.  
Performance per dollar is probably going to be a wash.  
So if you got 40 grand to drop on a TinyBox Pro...  
It is ready to ship.  
I will ship it to you today.  
We are out of stock of tiny box greens.  
I actually sold one that we don't even have yet already.  
So we're actually at negative one stock of greens.  
We've got a lot of reds.  
So also tiny box reds.  
Great choice.  
Someone bought one yesterday.  
I take it back.  
You made an excellent choice, sir.  
You have great taste.  

**Chenyu** [[01:00:15](https://www.youtube.com/watch?v=Ha4yFviaLps&t=3615)]  
All right.  
Thank you.  
See you next week.  
Bye.  
