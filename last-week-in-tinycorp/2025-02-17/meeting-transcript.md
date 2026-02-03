# 2025-02-17 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time (10pm HK time)
- company updates
- dsp / quantize
- reading group talk, bert (fusion, memory)
- scheduler
- driver
- tensor core
- onnx
- WebGPU (dawn, tinychat)
- other bounties (retinanet, rewrite 2.0)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=m7zQq40dr2M)

### Highlights

- [5090 orders](#geohot-000015) ordered $1 million worth of 5090s for TinyBox V2
- [Any CSS pros?](#geohot-004623) fix up tinychat CSS
- [Chenyu talk](#chenyu-000849) people are excited about porting to the web through WebGPU
- [Replace AMD](#geohot-010300) no more AMD software in our stack, almost

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=m7zQq40dr2M&t=0)]
Let's get started.
Any company update?

##### **Geohot** [[00:00:09](https://www.youtube.com/watch?v=m7zQq40dr2M&t=9)]
So we ordered, is my volume good?

##### **Chenyu** [[00:00:13](https://www.youtube.com/watch?v=m7zQq40dr2M&t=13)]
Ah, yes.
I can hear you.

##### **Geohot** [[00:00:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=15)]
Cool.
We ordered $1 million worth of 5090s.
Which doesn't get you as many 5090s as you think it should, but the order's in.
We have the first ones coming this week, too.
So we're going to build a TinyBox V2 with 5090s that we can start playing with.

##### **Chenyu** [[00:00:39](https://www.youtube.com/watch?v=m7zQq40dr2M&t=39)]
A lot of 5090s.

##### **Geohot** [[00:00:40](https://www.youtube.com/watch?v=m7zQq40dr2M&t=40)]
I mean, we'll see if Justin comes through with the Intel deal.
Is anyone interested in 15,000 Gaudi II cards?
Look, I think it's unlikely.
I think that it's.. If Intel was capable of doing things like this, they wouldn't be in the position that they're in right now.
But we'll see.
As long as I don't have to do anything.

##### **Chenyu** [[00:01:18](https://www.youtube.com/watch?v=m7zQq40dr2M&t=78)]
My impression is their habana lab was pretty legit.
They solved that right? So.

##### **Geohot** [[00:01:27](https://www.youtube.com/watch?v=m7zQq40dr2M&t=87)]
I mean, Intel has a long history of buying Nirvana, went to nothing, Habana, they're canceling Gaudi.
It's, yeah, the architecture is kind of upsetting too.
The Gaudi architecture looks very hard to use.
It's got a completely separate matmul engine that isn't programmable from the GPU-like cores.
So, it would be software that doesn't really belong anywhere else.
So, look, if we can get a phenomenal deal on them, I'll take them.
But I think that Gaudi is cancelled, and there's a reason why it's cancelled.
There's just no way anything in Torch could have ever been fast.

##### **Chenyu** [[00:02:16](https://www.youtube.com/watch?v=m7zQq40dr2M&t=136)]
Okay.
We're waiting on Intel.
That's not likely to happen.

##### **Geohot** [[00:02:23](https://www.youtube.com/watch?v=m7zQq40dr2M&t=143)]
We're waiting on Intel.
It's not likely to happen, but..
I'm open to it if they really want to give me a phenomenal deal on things with lots of memory bandwidth and RAM.

##### **Chenyu** [[00:02:41](https://www.youtube.com/watch?v=m7zQq40dr2M&t=161)]
Moving on to your stuff, DSP and quantize.

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=167)]
Yes, I've been making a lot of progress there.
It's a lot of good refactors, too.
All that de-vectorized stuff is eventually what I want to move to.
Some things force you to de-vectorize.
GPUs fundamentally force you pretty much to de-vectorize.
There are no vector units in GPUs.
But the more we can reason about vectorized, the faster it's going to be and the simpler the graphs are going to look until you do this explosion where you blow it up to the expand.
So yeah, working on the de-vectorized stuff.
I have two kernels fast.
I got one kernel up to 13 gigaflops.
The biggest thing holding back the speed right now is getting pad to work, getting the pad optimization to work.

##### **Chenyu** [[00:03:35](https://www.youtube.com/watch?v=m7zQq40dr2M&t=215)]
Work on what?

##### **Geohot** [[00:03:38](https://www.youtube.com/watch?v=m7zQq40dr2M&t=218)]
I mean, it works, but this is probably also why it's unbelievably slow on GPUs.
The problem is if you do a pad, all the consts become gated by that valid, even when you don't have to.
So for example, if you pad with something, that pad..
if you have a load where it loads a zero if it's invalid, and then you have a pad that is also applied to that load, it'll do another where on any consts, even though you're basically, let's say it's a multiply, even though you're basically multiplying by zero.
So the thing needs to be aware that if it's already zero, you can just multiply by the other value and you don't need a second gate on that.
I know what I have to do to write this, but that's just going to be the work next week.

##### **Chenyu** [[00:04:26](https://www.youtube.com/watch?v=m7zQq40dr2M&t=266)]
OK, great.
I probably have opened three separate issues or PR attempts on this.

##### **Geohot** [[00:04:35](https://www.youtube.com/watch?v=m7zQq40dr2M&t=275)]
Yeah.
So you've tried to fix this before.

##### **Chenyu** [[00:04:38](https://www.youtube.com/watch?v=m7zQq40dr2M&t=278)]
Yeah, that was the whole point for the previous discussion for rewriting the load into the where, but that doesn't really work.
That's effectively to solve that..
You can merge the valid.

##### **Geohot** [[00:04:54](https://www.youtube.com/watch?v=m7zQq40dr2M&t=294)]
Oh, to put the load into the where.
Yeah, that's probably a good thing to do first.
So there's like a bunch of refactors that the DSP stuff's currently on.

##### **Chenyu** [[00:05:05](https://www.youtube.com/watch?v=m7zQq40dr2M&t=305)]
Yeah, I noticed the same thing that, say, if you do a cat, a bunch of stuff is a separate where for individual ones, but you can combine them together.

##### **Geohot** [[00:05:16](https://www.youtube.com/watch?v=m7zQq40dr2M&t=316)]
Yeah, it's the same thing as cat, sure.
Yeah, being able to reason about these wheres in invalid with the loads, I think we can totally do that.
I think that like, yeah, I think we talked about this last meeting.
I know what the refactor has to be.
We basically want to gate the load.
We basically want to gate the load twice.
We want to gate the index to show that it'll never load from an invalid index.
And then we want to gate the actual value of the load.
And then all the normal value folding stuff will work.

##### **Chenyu** [[00:05:46](https://www.youtube.com/watch?v=m7zQq40dr2M&t=346)]
Yes.
We already have led folding rules in place.
Just, you just need to use it.

##### **Geohot** [[00:05:54](https://www.youtube.com/watch?v=m7zQq40dr2M&t=354)]
Oh, great.
So yeah, this is, this is probably not going to be the hard then.
Yeah.
A lot of it comes down to that.
I did, I'm through most of the quantize stuff.
So if you look at my PR min quantize for DSP, it's basically two things.
It's de-vectorize logic, which I want to make the default anyway.
And it's quantization logic, which is just, I learned about how quantization works.
I wrote, like, some basic stuff.
Like, in order to do this adjust, in order to, like, emulate a floating point thing, you do, like, a fixed point.
Yeah, like a fixed point.
You can see the rewrite rule for it.
So just getting those things tuned and to be right.
It's just all the normal quantization stuff.
I don't know how any of our quantization stuff is fast.
It's probably not.
We're probably just using floats and just the GPU happens to just be really fast.

##### **Chenyu** [[00:06:45](https://www.youtube.com/watch?v=m7zQq40dr2M&t=405)]
Yeah, so we have the NF4 quantize for LLaMA.
That's very, very slow.

##### **Geohot** [[00:06:51](https://www.youtube.com/watch?v=m7zQq40dr2M&t=411)]
Oh, yeah.

##### **Chenyu** [[00:06:54](https://www.youtube.com/watch?v=m7zQq40dr2M&t=414)]
I think int8 is probably fine, but we are not doing the block.
So our Int8 is kind of broken, too.

##### **Geohot** [[00:07:05](https://www.youtube.com/watch?v=m7zQq40dr2M&t=425)]
Well, yeah.
I mean, even if, like, with Int8, it's still going to give you the GPU memory bandwidth.
So if you're doing batch size 1, you are going to have the memory bandwidth if you have working Int8, even just on the loads, even if the first thing it does is convert it back to float.
But the DSP can't convert it to float, so.
Yeah.

##### **Chenyu** [[00:07:25](https://www.youtube.com/watch?v=m7zQq40dr2M&t=445)]
Cool.
We got six weeks left.

##### **Geohot** [[00:07:29](https://www.youtube.com/watch?v=m7zQq40dr2M&t=449)]
It'll be doable.
It's a good project.
Everything about this is just like, you have to get everything right to make the DSP work.
Whereas with GPUs, you can kind of, they're so forgiving.
Like there is nothing more forgiving than an NVIDIA GPU to get you performance no matter what.
Their compiler is so good.
Their programming model is so good.
Like you can write, I mean, I guess this is why they're so popular.
You can write basically bad code and still get performance.

##### **Chenyu** [[00:07:58](https://www.youtube.com/watch?v=m7zQq40dr2M&t=478)]
Isn't that nice?
So I want people to write OK-ish tinygrad front-end code and still be fast.

##### **Geohot** [[00:08:06](https://www.youtube.com/watch?v=m7zQq40dr2M&t=486)]
Yeah.
I mean, we want to replicate that property of the NVIDIA code.
But the DSP, even when I'm done with this DSP contract, yeah, we're going to get MobileNetv2 to be fast.
But it's going to still take a lot of work to get everything to be fast on the DSP.
But almost everything I'm doing here is universally applicable to speed, period.
Making pad work, I think, is just a universal.
It helps everything.

##### **Chenyu** [[00:08:29](https://www.youtube.com/watch?v=m7zQq40dr2M&t=509)]
Yes.
I want to see that pad happening.

##### **Geohot** [[00:08:34](https://www.youtube.com/watch?v=m7zQq40dr2M&t=514)]
Yeah.
And then these quantization rules also should work for, it should be pretty easy to get NVIDIA Tensor Cores working as well.
So we could use Int8 Tensor Cores, which will get us the massive gigaflops, massive teraflops, 600 on 4090s.

##### **Chenyu** [[00:08:49](https://www.youtube.com/watch?v=m7zQq40dr2M&t=529)]
Sounds good.
OK, moving on.
I gave a talk or went through the TinyGrad codebase yesterday.
I put a slide in documentation channel.
I think people are generally pretty excited about works like this.
I guess the main takeaway.
People in the group are interested in WebGPU and porting things to web.
And I mentioned about the export and the TinyChat demo.
So I think that definitely will be one way people interact with WebGPU and with TinyGrad.
Like, they can load the ONNX model and run it in web.

##### **Geohot** [[00:09:43](https://www.youtube.com/watch?v=m7zQq40dr2M&t=583)]
Great.

##### **Chenyu** [[00:09:44](https://www.youtube.com/watch?v=m7zQq40dr2M&t=584)]
That's the main thing.
So for BERT, sorry.

##### **Geohot** [[00:09:53](https://www.youtube.com/watch?v=m7zQq40dr2M&t=593)]
If we go to the library for that, that's great.
That's a pretty big niche.

##### **Chenyu** [[00:10:01](https://www.youtube.com/watch?v=m7zQq40dr2M&t=601)]
Yeah.
I think WebGPU, I guess it just runs on people's power in browser, and they don't need to set up their environments and stuff.

##### **Geohot** [[00:10:12](https://www.youtube.com/watch?v=m7zQq40dr2M&t=612)]
This is why the web took over.

##### **Chenyu** [[00:10:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=615)]
Yep.
So we can talk about that more in the WebGPU part.
BERT, so I run a bunch of runs.
I fix some regressions.
Now I think our speed is, although speed is comparable to our last submission, per step is 2% slower.
I think some of it is search, because we introduce different shapes of TensorCore.
We also remove multi-output.
But the kernel looks similarly bad, and a lot of time I'm spending on really just attention.
So two main direction that improves BERT would be better kernel fusions and better understanding where we spend in memory.
If we can fit larger batch size, it will certainly be faster.

##### **Geohot** [[00:11:10](https://www.youtube.com/watch?v=m7zQq40dr2M&t=670)]
I suspect that we waste a ton of memory storing the wrong Dtype.
Like we're storing floats when we should be storing float16s.

##### **Chenyu** [[00:11:20](https://www.youtube.com/watch?v=m7zQq40dr2M&t=680)]
That's cast before view.
Yes.

##### **Geohot** [[00:11:24](https://www.youtube.com/watch?v=m7zQq40dr2M&t=684)]
Yeah.
And all variants.
There's tons of variants of cast before view.

##### **Chenyu** [[00:11:29](https://www.youtube.com/watch?v=m7zQq40dr2M&t=689)].. so from one realized to another realized.
Basically, you can pick the thing in the middle that has the smallest Dtype and to store that.

##### **Geohot** [[00:11:43](https://www.youtube.com/watch?v=m7zQq40dr2M&t=703)]
Yeah, we basically need that logic.
We have that same, it has the same problem.
So I wrote that don't realize expands and just put manual contiguouses in the DSP stuff, but it's not good.
It's not right.
It should be, the scheduler should figure that out.

##### **Chenyu** [[00:12:02](https://www.youtube.com/watch?v=m7zQq40dr2M&t=722)]
And there's a separate tricky stuff.
It's probably specifically to TensorCore, because we can only trigger TensorCore if its parent is safe to pad.
So we pad that thing and do TensorCore.
But you can imagine if we.. up to the kernel at the wrong point, maybe your TensorCore previously can be triggered, but no longer can be triggered.
I don't have a good solution for that, but that's the main reason why if we just blindly put don't realize a lot of things get slower because tensor core don't over trigger.

##### **Geohot** [[00:12:39](https://www.youtube.com/watch?v=m7zQq40dr2M&t=759)]
So there's a way to fix that.
What you can do is you can inject a where before the tensorcore to re-inject zeros wherever you padded.

##### **Chenyu** [[00:12:51](https://www.youtube.com/watch?v=m7zQq40dr2M&t=771)]
But what if it's not a clean pad?

##### **Geohot** [[00:12:56](https://www.youtube.com/watch?v=m7zQq40dr2M&t=776)]
It doesn't matter.
If something is unsafe in pad, let it be unsafe in pad, every element-wise.
This is the real solution to unsafe pad.
What you can do is you can have a big chain of things.
The worst unsafe pad is going to do is end up with something non-zero, and then you stick a where at the end of that and put the zeros back in.
Yeah, this is the universal solution to unsafe path.

##### **Chenyu** [[00:13:28](https://www.youtube.com/watch?v=m7zQq40dr2M&t=808)]
I can write that.
OK, that sounds very good!!!

##### **Geohot** [[00:13:31](https://www.youtube.com/watch?v=m7zQq40dr2M&t=811)]
Yeah.

##### **Chenyu** [[00:13:33](https://www.youtube.com/watch?v=m7zQq40dr2M&t=813)]
OK, great.
Yeah, but OK, that sounds good.
Yeah, anyway, BERT is important because BERT is very clean.
It really is the same thing as other LLM training.
We just need to make that kernels fast, and it will be fast.

##### **Geohot** [[00:13:54](https://www.youtube.com/watch?v=m7zQq40dr2M&t=834)]
Yeah, attention fusion.
Attention fusion is going to be harder.
Like even softmax fusion is sort of beyond what we can express right now.
But focusing on these pads and the Dtype things, I think is a very good place to focus.
And I'm struggling with the same stuff right now for the DSP.

##### **Chenyu** [[00:14:11](https://www.youtube.com/watch?v=m7zQq40dr2M&t=851)]
Okay, sounds good.
Yeah, I think we could at least do the first part of softmax fusion is really similar to a norm fusion.
You do a reduce, then you subtract that, or you do a max and you subtract that.
I think that thing should be doable, maybe after the next schedule clean up.
But the whole thing, I don't know how to do it.
But the whole thing of softmax.
The whole thing of softmax fusion is similar to argmax fusion.
You want to track a value that depends on another value that's being looped over that we cannot express yet.

##### **Geohot** [[00:14:57](https://www.youtube.com/watch?v=m7zQq40dr2M&t=897)]
I looked at softmax fusion, and I posted one of the graphs.
The main thing that you have to do is you have this reduce.
and you have to put the reduce in locals.
It's the genericization of group.

##### **Chenyu** [[00:15:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=915)]
So there are two softmax optimizations I was thinking.
So one is the same kernel that we have now, and it's the thing you just described.
But there's a way, and we probably need to do this.
So it looks more like argmax.
So it's a two-pass algorithm on softmax.
That's a different kernel than what we have now.
I think we need that for flash attention, because flash attention is basically that.

##### **Geohot** [[00:15:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=947)]
We can't even do simple reduce grouping.
But yeah, I know the argmax that you bring up.
I can come up with a solution to that if you think you can do the softmax reduce one.

##### **Chenyu** [[00:16:01](https://www.youtube.com/watch?v=m7zQq40dr2M&t=961)]
And you learn a lot more about scheduler first.
OK.
I think it's a good time to move on to scheduler.

##### **Qazalin** [[00:16:13](https://www.youtube.com/watch?v=m7zQq40dr2M&t=973)]
So we have kernel opt now.
Reload is gone.
You can basically let assigns depend on other signs, which is a nice refactor.
It did regress speed by 10%.
But overall, it's a simplification.
It does set the stage to move on to the big const map refactor.
So what we have to do really for reorder expand is the reconstruction of movement ops from views, like genericize that logic.
We have that logic.

##### **Geohot** [[00:16:46](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1006)]
Whoa, whoa, whoa.
That's impossible.

##### **Qazalin** [[00:16:49](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1009)]
I'm not going to do that.
I'm not going to sit and do math.
I'm just going to brute force it for the tensor map.
That's the plan.

##### **Chenyu** [[00:17:00](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1020)]
When you say you need to reconstruct, it's really just reconstruct.
You are not arbitrarily creating a view and try to figure out a set of movement ops.

##### **Qazalin** [[00:17:11](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1031)]
We know the movement ops.

##### **Chenyu** [[00:17:13](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1033)]
Yeah, so if it's coming from some source that we are already aware of, at least you can have a mapping between your set of movement ops to the view, then just look up that.
I think that's fine.

##### **Geohot** [[00:17:27](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1047)]
Oh, yeah, just use a cache if you want to do it in the same function.
Just cache whatever you turned into a view, and then you can re-expand that to movement ops.

##### **Qazalin** [[00:17:35](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1055)]
It's not that simple.
There's edge cases, but I'm going through the edge cases.
I think that should be enough to enable all of these.
So yeah, I'm going to merge your reorder expand this week.
And I'm going to start work on more fusion stuff in the scheduler.

##### **Geohot** [[00:17:52](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1072)]
I'm really excited for reorder expand, because that's cast before view.
That's all of the stuff.
Oh yeah, I forgot I did this this week, yeah.
That expand, the early reorder expand is basically the prereq for softmax.
That's how I ended up there.
Oh, great, yeah, no, I see you've got the kernel that merged too.
Sorry, the program renderer.
You're very fast with those JavaScript things.
Yeah, so I'll get that merged tomorrow.
And then I'll finish up kind of my refactor of rewriter and all that stuff into something that I want to call flow.
Oh, do you know what I said about the schedule, like the create schedule from names?

##### **Qazalin** [[00:18:50](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1130)]
I haven't done that.
Yeah, yeah.

##### **Geohot** [[00:18:53](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1133)]
Yeah, but you understand what the idea is.
And then also having something in graph rewrite where I can name the rewrite.

##### **Qazalin** [[00:19:06](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1146)]
I did merge the fast viz, though.
I don't know if you've tried Beautiful MNIST yet with the new viz.

##### **Geohot** [[00:19:13](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1153)]
Oh, I haven't tried.
I see the way that they light up now when they load.
It's really nice.

##### **Qazalin** [[00:19:20](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1160)]
Yeah, yeah, yeah.

##### **Geohot** [[00:19:22](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1162)]
Yeah.
No, that's awesome.
Great.
So you're telling me Beautiful MNIST works right now if I try that in viz?

##### **Qazalin** [[00:19:29](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1169)]
Yep

##### **Chenyu** [[00:19:32](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1172)]
Oh, one thing I forgot to mention.
So during the talk I gave yesterday, people are also excited about the fact that you can just debug equals to 2 and debug equal to 4 and see the source code.
And also viz equals to 1 is pretty nice.
Or understanding what's happening in TinyGrad.

##### **Geohot** [[00:19:50](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1190)]
Oh, I finally made debug equals 3 usable, too.
Debug equals 3 will show you the buffers for each kernel.
It doesn't print tons of UOp spam.
It's just the buffers.
So that should be useful for us.

##### **Chenyu** [[00:20:03](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1203)]
Do we print that by default in like five or higher ones, or no?

##### **Geohot** [[00:20:07](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1207)]
Everything that prints in three prints in five or higher.

##### **Chenyu** [[00:20:12](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1212)]
No no no.
I mean, but you remove the ones that prints the modify UOp, right?
And we don't currently print that anywhere else.

##### **Geohot** [[00:20:20](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1220)]
Oh, yeah, remove that if you want that back.
I think maybe someone put it back.
If you want it back, just throw it in, but not three.

##### **Chenyu** [[00:20:28](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1228)]
No.
Yeah, so I added a row at AST.
I find that useful in writing tests.
But my issue with the big UOp was it can get very big, very long, very easily.
DEBUG equals to 4 code, it's kind of always short.
And at least it's compact.
And it doesn't break my indentation on my screen.
Okay.
Oh, that's great.

##### **Geohot** [[00:20:59](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1259)]
Yeah.
Its a stretch here.
It's taking, it's taking about 20 seconds to load.

##### **Chenyu** [[00:21:09](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1269)]
Does it work?

##### **Geohot** [[00:21:12](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1272)]
Oh, it's still loading.
Nothing yet.
Oh, but can I click over to the other one?
I mean, I guess what I'm also fine with is if I could just click away from it really fast.

##### **Qazalin** [[00:21:29](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1289)]
Yeah, the issue is with the rendered, with the graph that we have.
So that's like the last bottleneck on this whole thing.
It's rendering SVGs and SVGs are just blocking the main thread.
That's slow.
I have something that uses the GPU to do it.
That will fix it.

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1312)]
A lot of times with UI stuff, like the problem is right now.
So I run on Beautiful MNEST.
I click create schedule with VARS 1.
And now the thing is hung.
I have no feedback.
I have a black screen.
I have some feedback in the Python window, but if I click over to something else, it looks just entirely wrong.
Now it let me click away to something else, but nothing's loading still.
Because it had to wait for the Python to finish the kernel thing.
And then it finally loaded.
But you see what I mean?
Like there always has to be something moving on the screen telling me what's going on.
Every time I'm at a black screen, like I don't know if I can click other things.
I don't know if I can.
So yeah, like run beautiful MNIST, click that.
Like I want to have something on the screen in like a second after I click create schedule with vars one.
I don't really care what it is as long as it's responsive.
Like if we can't render the graph, we can't render the graph.
But that responsiveness is super important.
Yeah, it's kind of annoying that when you expand it, it automatically loads the first one.
That makes a lot of sense.
But the problem is the first one is this huge one on the schedules.
So it was my hack to just not make the first one the main one.
But yeah.
Whatever it is, here's the test to do.
Run beautiful MNIST with Viz, and then click that Create Schedule.
And then I want something on the screen in a second.

##### **Chenyu** [[00:23:43](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1423)]
You want the loading bar?

##### **Geohot** [[00:23:49](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1429)]
That's better.
I really want something that doesn't make the whole UI unresponsive.
Even if I could just click on it and then click away to something else and that is under a second, I'm OK with that too.
The problem is right now when I click it, it takes 18 seconds to return that thing from Python.
So I don't know if there's a way to interrupt it or.

##### **Qazalin** [[00:24:29](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1469)]
Yeah, I think I know what I need to do for that.
But it all comes down to fixing the graph renderer.
That's blocking everything at this point.
It's bothering me.

##### **Geohot** [[00:24:44](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1484)]
it actually blocks them in thread.

##### **Qazalin** [[00:24:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1487)]
Yeah.

##### **Geohot** [[00:24:48](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1488)]
And you can't get you can't get inputs to give you can't cancel it in any way.

##### **Qazalin** [[00:24:55](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1495)]
Not really.
It's not like a worker or something.
It's just like a black box library that's calling some tag or anything.
I have one thing that needs it to work.

##### **Geohot** [[00:25:07](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1507)]
Yeah, I'm an old school JavaScript guy.
What if you do like a window dot set timeout?

##### **Qazalin** [[00:25:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1515)]
I'll try it.

##### **Geohot** [[00:25:19](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1519)]
And then some way to interrupt the, so the Python thing takes 18 seconds.
Is there, can that be interrupted?
I'm sure that can be interrupted.
Like interrupt the Ajax.

##### **Qazalin** [[00:25:30](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1530)]
Yeah.
I refactored it to like stream stuff so we can actually just cancel it midway.

##### **Geohot** [[00:25:36](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1536)]
Right.
Yeah.
I mean, it's like, like, like all I do, 90% of what I do, whenever someone like asked me to like test their thing is I'll load it up and they'll just click around really fast and be like, I broke it.
And then, then after I click around really fast, if I didn't break it, I'm like, okay, this is good software.
This is something I want to use.

##### **Chenyu** [[00:26:03](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1563)]
Yeah.
That's good.
We know what needs to be tested, and we can move on to move on.

##### **Geohot** [[00:26:11](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1571)]
It's actually awesome that this works at all.
This is so cool.
That's like, OK, fine, it takes 30 seconds to load.
But yeah, great work making this work.

##### **Chenyu** [[00:26:23](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1583)]
Cool.
I will also try it after the meeting.
OK, let's move on to driver.

##### **Nimlgen** [[00:26:33](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1593)]
yeah so i'm also focused on the the nv gpu this week um so yeah actually we got only four versions to this thing um like okay so we also can send tilts now right on the monitor but they're still slow so yeah so i'm just looking into somewhere and um
Yeah, actually, they use.. I found and localized all this stuff.
They set up NVMe queues and how they talk to the NVMe drive.
So, yeah, actually, they also use TLB to set up to write some information into the bar.
But after that, it looks like they set up queues and these queues.. It looks like queues
find their memory, like on the controller itself.
And it looks like has access to this memory.
So yeah.

##### **Geohot** [[00:27:48](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1668)]
Wait, wait, wait.
Sorry, I'm not totally following this.
So first off, do we have the 24 to where the 23 is?
So does the GPU on Tiny10 work?
Can I use that, even if it takes like six seconds or whatever?
Or six minutes?

##### **Nimlgen** [[00:28:03](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1683)]
I'm not sure about Tiny10, but on the.. But yeah, yeah, we can send the TLB.
It's just the state where we can.. So yeah, it's actually the same state as Tiny10.

##### **Geohot** [[00:28:16](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1696)]
Well, yeah, but I'm on Tiny10 right now.
Do you have a branch I can try?

##### **Nimlgen** [[00:28:22](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1702)]
Yeah, I mean.. Yeah, actually, I mean, there is full request to try, but it's just..
not loading them completely.

##### **Geohot** [[00:28:41](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1721)]
I'm checking out GPU USB on master.
Yeah, cool.

##### **Nimlgen** [[00:28:50](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1730)]
So, so yeah, it's actually the portal is still peer request 24.
So yeah, it can do the same thing as right.

##### **Geohot** [[00:29:03](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1743)]
I'm rebasing.
Let's hope this rebase works.
This rebase does not work.
I'm so bad at Git.
There's just a conflict in the imports.
That's easy.
So then, do you think it's doable without firmware mods?
Or do you think we're going to have to change the firmware on the thing?

##### **Nimlgen** [[00:29:42](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1782)]
So I'm still looking into that.
I'm not really sure about the USB subparts of this firmware.
It's actually how it could talk to the USB controller and just take all the data.
So yeah, I'm going to look into that.
But yeah, I think even if we don't find anything good, I think we can just modify the firmware and actually move all this logic that we have right now into the firmware itself, which would be a lot faster.

##### **Geohot** [[00:30:30](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1830)]
So I understand modifying the firmware will make it faster, but the question is how fast?
Like, sure, we'll definitely be able to do whatever this USB transaction is a lot faster.
But I worry that we're not going to be able to get like multi gigabit speeds, which is really what I want.

##### **Nimlgen** [[00:30:51](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1851)]
Yeah.
I mean, actually, what I measured right now, there is actually some internal function already, which is implemented in different way, which can read some external memory.
So the speed of this is about one megabyte a second.

##### **Geohot** [[00:31:10](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1870)]
One megabyte a second.

##### **Nimlgen** [[00:31:11](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1871)]
Yeah, yeah, yeah.
It's not very fast.
And actually, I think that matches because I found that the controller runs on 25 megahertz.

##### **Geohot** [[00:31:28](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1888)]
We've got to set up some way to bypass the controller entirely, right?
We have a lot of control of the GPU, too.
So if we could get the GPU to pretend to be an NVMe device,
Like, there's no way the, it's using like PIO is the old term for it, like programmed IO, where you do the copy one at a time.
There's no way that that microcontroller is doing basically a mem copy for an NVMe drive.
There has to be some kind of DMA you can set up.

##### **Nimlgen** [[00:32:05](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1925)]
So actually, yeah, that's interesting.
I mean, yeah.
I mean, I found, like, yeah, all this NVMe logic, yeah, like, the addresses they set and the queue they set, so, and addresses actually look a bit strange, but actually, as far as I understand that, the whole idea of the NVMe is just it's, like, you can do DMA to the device.
Actually, yeah, okay, I'll check that.
I'm not sure what addresses they set there yet.

##### **Geohot** [[00:32:40](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1960)]
Yeah, the NVMe has to be fast in both directions, right?
Like, when you use these things with NVMe drives, they're fast on both read and write.

##### **Nimlgen** [[00:32:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1967)]
Yeah.
Yeah, yeah.

##### **Geohot** [[00:32:53](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1973)]
OK.
libusb equals 1, amd equals 1.
OK, I need to apt-get install libusb.
How does libusb talk to the kernel?

##### **Nimlgen** [[00:33:18](https://www.youtube.com/watch?v=m7zQq40dr2M&t=1998)]
That's a good question.
I don't know.

##### **Geohot** [[00:33:22](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2002)]
Oh, so, okay.
It's not, I need, I don't have libusb 1.0.
Do you not have to ask for that?
Oh, libusb 1.0 dev.

##### **Nimlgen** [[00:33:37](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2017)]
Yeah.
Actually, yeah, maybe this branch is not in the best state right now.
I don't know.

##### **Geohot** [[00:33:48](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2028)]
Is there any way I can, anything I can test?
Yeah, if I run it right now, I get, yeah, this branch isn't right, because I'm getting ASM got an unexpected keyword argument is 24.

##### **Nimlgen** [[00:33:58](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2038)]
Okay, yeah.
Yeah, okay.
I'll update this branch to the working state.

##### **Geohot** [[00:34:19](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2059)]
Yeah, what I want to do is, even if it takes a long time, even if it's still slow transactions, I just want to see this work on TinyTest with the 20.
So it's an ASM24 and it's a 7600.

##### **Nimlgen** [[00:34:29](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2069)]
Yeah, I'll take a look.

##### **Geohot** [[00:34:41](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2081)]
Yeah, and then there has to be.. Before we modify the firmware, I really want to understand how this NVMe drive is doing it.
Because any modification to the firmware is going to be limited by that 25 MHz clock speed that you're talking about.
Whereas if we can actually get the DMA to trigger off the thing, DMA is fast.
Like, it has to be.
Because this thing can plug into a MacBook and get 40 gigabits.
You can even get 20 gigabits on just USB 3., 3.2.
So yeah, there's got to be there's got to be some way to do this that isn't.
What else could PCIe be besides like a DMA to an address?

##### **Chenyu** [[00:35:42](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2142)]
to update the branch to a state that can be tested on tiny10.
Let's move on to Tensor Core.

##### **Ignaciosica** [[00:35:54](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2154)]
Hi.
Hello.
I don't have much progress to report?
I have been mainly working on some tests and proof of concepts, but don't have anything worth upstreaming.
I have some questions, though, to which is the correct abstraction.
Is there another use case I could take into consideration to make this abstraction generic?
I don't want to overfit into the AMX implementation.

##### **Geohot** [[00:36:26](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2186)]
Yeah, so it's anything where you have a.. It basically almost should be the same thing as Define Local.

##### **Ignaciosica** [[00:36:35](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2195)]
Okay.

##### **Geohot** [[00:36:36](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2196)]
Yeah, whatever abstraction you use should actually kind of work with Define Local as well.
And you can have a flag on Define Local if it's like a special local.
Because that's basically what you're doing.
You're loading and storing from a local, which is the AMX register, which is free.
So yeah, it's the same thing as Define Local.

##### **Chenyu** [[00:36:59](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2219)]
True.

##### **Geohot** [[00:37:03](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2223)]
Yeah, we'll see if these, I'm not sure, flammit says the 5090 doesn't have it, but it seems like Tensor cores are going to start to have stuff like this.
So yeah, it's the same basic idea as local memory.
And if you really want to go far with it, like unify the concept of like all the buffers, right?
So we have define ACC.
define ACC, define local, and define AMX can all kind of be one thing.
Define ACC is really define register.

##### **Ignaciosica** [[00:37:37](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2257)]
Yes.

##### **Geohot** [[00:37:38](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2258)]
And then assign a store.
Then you should load as well.
Yeah.
Yeah, that needs to be refactored.
Define ACC.
It should be the same thing as define ACC.

##### **Ignaciosica** [[00:37:53](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2273)]
Yes, like
One problem I encountered on the AMX is that it has a fixed continuous access size.
That's why mainly I was thinking in a more complex definition, like a data class with size, continuous access, and Dtype.

##### **Geohot** [[00:38:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2295)]
If it can only be accessed as one thing, just make that the Dtype.
Make that the Dtype and don't support GEPs on that.

##### **Ignaciosica** [[00:38:21](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2301)]
Oh, that's a good idea.
Yes.
Thank you.

##### **Chenyu** [[00:38:22](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2302)]
That's good.
Any update for ONNX?
Okay.
Implemented Attention, blah, blah, blah.

##### **Geohot** [[00:38:48](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2328)]
Wait, how is it passed 201, failed 49 in the top 100 HuggingFace repos?

##### **Chenyu** [[00:38:56](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2336)]
Are you testing 250?
Yeah.

##### **Geohot** [[00:39:00](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2340)]
Oh, multiple.

##### **Chenyu** [[00:39:08](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2348)]
So 250 in total.
So if it's a numerical issue, it's probably fine.
But is there any main thing that is not implemented?

##### **Geohot** [[00:39:16](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2356)]
I'm actually, I'm not so sure it is fine, depending on what that means for numerical inaccuracy.
Because that thing is really, the quantized linear is really fidgety.
And like it's using a round right now, and I'm not 100% sure that's right.
So I have another thing that also works besides the round, but if you get this a little bit wrong, it degrades accuracy.
So I'm curious what exactly those representations are.
It's also possible that the ONNX runtime implementation of quantization is numerically inaccurate.
There's all kinds of..
I dove deep into quantization.
I think, I guess it's fine if they're not.
It's not really the ONNX being broken, but there's a lot of subtlety.

##### **Chenyu** [[00:40:03](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2403)]
My point for fine is fine to make a PR and merge this into master because I know you are working on the contact stuff.
That can be like fixed.

##### **Geohot** [[00:40:12](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2412)]
Sounds good.

##### **Chenyu** [[00:40:14](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2414)]
Independent of this script and for this bounty.
I think the scope of a bounty is we get things merged.
We test the popular repos.
And if there's no obvious thing that we don't support, I consider that done.
Then we can fix the specific for these quantized stuff.

##### **Geohot** [[00:40:40](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2440)]
Yeah, agreed.
Agreed.
I just want to say that I think the Quantize things are real bugs, but I think they're outside the scope of the bounty.
I agree.

##### **Chenyu** [[00:40:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2447)]
Cool.
Blow up after multiple rounds of quantize.
I think some of these would be interesting if you also mark or have a specific way to show these errors in your script, like known numerical arrows you can test or fix and see
compare to see if it's like ONNXRUNTIME has an issue, because we know sometimes it can have issue, or if it's our implementation that's incorrect.
Cool.
OK, WebGPU split into Wpmed first.

##### **Wpmed** [[00:41:33](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2493)]
Yeah, so on the GPU front, yeah, the FP16 stuff has been merged.
There was a rough actor that's merged, and I also added synchronize because testing spped stuff, I get really interesting results, like faster than metal on Torch.
So it was suspicious.
I checked with Nimlgen, and yeah, it was missing synchronize, so I added it.
So we bumped into this issue where we tried to split dims because the global dims became too large to fit in WebGPU limits.
So it always errored out.
Now it's solved.
It has been merged.
So yeah, WebGPU is in a lot better shape than it was last week.
So now I will move on to actually working on the export model stuff.

##### **Chenyu** [[00:42:26](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2546)]
Can you fix the library path?

##### **Wpmed** [[00:42:30](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2550)]
No, that one not yet.
Yeah, because I will fix it.
It's just that when I brew install it, it finds it.
But maybe that's something I. So you brew install it, and it doesn't find it, right?

##### **Chenyu** [[00:42:51](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2571)]
Yeah, so brew install install in the opt slash homebrew slash lib.
But my ctype.findlibrary is not in my default path.
So I can either add it to the path, or I manually specify the path.
But the main point is that in terms of the errors we are giving, it's not accurate.
I followed it, but it's still not working.

##### **Wpmed** [[00:43:19](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2599)]
Yeah, I will fix it then first, and after that, export all that stuff.

##### **Geohot** [[00:43:25](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2605)]
Cool.
Oh, that's nice.
It's nice that you bring back the split in test and stuff.

##### **Wpmed** [[00:43:34](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2614)]
Yeah, it was driving me crazy that everything worked, and benchmark was always just timing out.
And yeah, it was because..
Because group dims was not just for.. So at first I thought the original limit dims was just for when you have a 4D global dim and you want to limit it to 3D, but it was not just for that.
So it can also group together dims when..
when the global max length is equal to your dims length.
And it errored out because on NVBeam, it chose the split dim strategy, which is slower.
So that was the reason.
But now the two work perfectly well together.
So it solves the WebGPU stuff, and it works fine on NV as well.

##### **Chenyu** [[00:44:33](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2673)]
Great.
Do you know what's the limit for buffer numbers for WebGPU kernel now?
Is it 10 on layers?

##### **Wpmed** [[00:44:40](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2680)]
It's 10 or 11.
I think it's 10.

##### **Chenyu** [[00:44:45](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2685)]
Is there a way that we can increase that?

##### **Wpmed** [[00:44:50](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2690)]
So I don't know why 10, actually.
Because WebGPU is a layer on top of Metal if you run on a Mac.
And in Metal, you don't have
You're not limited.

##### **Chenyu** [[00:45:01](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2701)]
Metal is 32, right?
32 or 31.

##### **Wpmed** [[00:45:04](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2704)]
Yeah, but I think it's larger.
So on metal, I think it's larger than 10.
It's more like 20 or more.
And then in the original.
32 on metal, I think.
Yeah, it's much larger.
So not sure why they limit it like that.
The thing with VGPU-Pi that we previously used is there is no such limit, but the trap there is, so you think you're fine and then you export your model and then you run it in Chrome and then you see that, oh, it doesn't work.
So what we see now is like the reality and VGPU-Pi was not exactly WebGPU, but..
I don't know.
So you can request these limits.
You can try requesting larger limits.
But for this buffer number, I couldn't request larger.
If I try to request larger, it errored out.
So it seems like it's done.

##### **Chenyu** [[00:46:06](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2766)]
Oh, that's fine.
Just curious.
Cool.
Yeah, so for the tiny chat, there's an implementation link in general channel.
Do you want to say something?

##### **Geohot** [[00:46:23](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2783)]
It's impressively fast on my Mac.
By the way, if anyone in here is a designer who wants to mess with the CSS of this, when I make the window smaller, there's no padding to the edge of the chat bubbles.
I'm terrible at this, but if someone here wants to fix up the CSS..

##### **Chenyu** [[00:46:59](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2819)]
Setting up the code for merge sounds good.
Yeah, the demo works fine.
I also tested it on my phone and my browser, and it seems to be working.

##### **Geohot** [[00:47:10](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2830)]
Yeah, we need a designer to make this look nice.

##### **Chenyu** [[00:47:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2835)]
Well, Wozeparrot would be sad if you say it doesn't look nice.

##### **Geohot** [[00:47:21](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2841)]
Oh, well, we've moved far away from the original Wozeparrot, the red and the green.
Half of me wants to just copy ChatGPT exactly.
No, I think it's fine.

##### **Chenyu** [[00:47:35](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2855)]
I heard LLMs are pretty good at copying style nowadays.

##### **Geohot** [[00:47:44](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2864)]
But you know, it's fast, it's local.
The tokenizer is uncached, though.
So it has to go to the internet every time to get the tokenizer.
Any reason that can't be just shoved into NextDB, too?
Yeah, I mean, again, you've gone above and beyond what this bounty is.
This definitely already qualifies once it's merged.
But it would be great to have it work without internet.
I think you mentioned that.
So if you just go to the ones.
Yeah, no, I think when this is final and we have good design and this is good, I think that this is going to work.
hit the front page of Hacker News, and this is your accomplishment.
This isn't TinyGrad's accomplishment.
This is like the use of TinyGrad as a library, which is awesome.
And I think that there's a lot of excitement around WebGPU, and this could be like a first sort of niche that we've really just tried our best in.
It's exciting.
Let me know when you want me to review any of the code.
Breaking things up into PRs is always good.
Independent, standalone features is a lot easier to review than lots of lines.
but lots of lines can be okay if they're not.
Like lots of changes all around the code base is impossible to review.
Let me see what the PR is now.
Oh yeah, it's very few changes to the actual code base, but those LLaMA changes should be a separate PR.
Yeah, like all the changes to llama3 export model and LLaMA should be a separate thing.
And then like all of your JavaScript stuff can, I will review it, but the stuff that I'll review most carefully is stuff that changes existing code.
Cool.

##### **Chenyu** [[00:49:53](https://www.youtube.com/watch?v=m7zQq40dr2M&t=2993)]
Nice work.
Okay.
Let's move on to other bounties.
Retinanet.

##### **Flata** [[00:50:01](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3001)]
Hello.
So for retina net, I've been trying to figure out where the lands are coming from.
So I've been working on a very sample set of the data set.
And at least for this one, because there's two losses involved, the classification loss and the regression loss.
So on the classification loss side of things,
on the smaller set, it will actually nan out.
But on, I guess, a bigger batch size, it's the regression loss that's nanning out.
So I'm trying to focus on the smaller set size of the data set.
And for some reason, the backbone model, which is the resnet size, is
Throwing out some NANs later on, once, you know, once NS trained a few epochs or so, probably like, I think more than 20 epochs.
So I'm trying to figure out where that is coming from.
So still investigating on that.
I did find some bugs along the way as well, just kind of like in some places here and there.
So that was a good time that I was able to adjust those, but mainly focusing on figuring out where the NANs are coming from now.

##### **Chenyu** [[00:51:04](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3064)]
What's your process look like figuring things like this out?
So you've mentioned you train in float.
It's less likely to be like float16 issue.
But other than that, how do you debug this?
Because we want to kind of bake this into Tinygrad as a debugging feature.
So just curious how you are currently doing it.

##### **Flata** [[00:51:28](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3088)]
I think definitely debugging with a smaller data set did help a lot for me.
I guess my cycle time on that is actually pretty short.
What else am I even using?
I think mostly that and really just kind of digging through the model.
I don't know if there was, I guess, any other helpful tips that I had there.

##### **Chneyu** [[00:51:52](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3112)]
For BERT and for ResNet, because I think it's BERT, BERT has the global norm clipping stuff.
So it clips the global norm of gradients.
So for that, I just output it as another value in addition to the loss.
And I also print that in WnB.
And you can see the global norm should be increasing.
gradually then decreasing as the learning rate gets smaller.
So maybe something similar to that will help.
I don't know if you have similar normalization numbers in your.
So one obvious thing is you can print the scale of your gradients.
So if gradients become too large, then something is broken similar to that.

##### **Flata** [[00:52:44](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3164)]
Oh, yeah, that's definitely a good point.
Yeah, I also did actually do something like that, similar to what you said, just kind of printing out the values along with the loss for the certain parts of the network.
And that's kind of where I found out where the backbone itself was throwing out the NANs, not the actual classification head, in this case, that was causing it.

##### **Chenyu** [[00:53:05](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3185)]
OK, sounds good.
And you shouldn't have any issue with accessing the machine?

##### **Flata** [[00:53:13](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3193)]
No, not at all.

##### **Chenyu** [[00:53:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3195)]
Great, good to know.
OK, let's move on to graph rewrite 2.0.

##### **Ttomsa** [[00:53:27](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3207)]
Hi.
So I guess it's almost over.
I tested.
I did the name assignment.
And it said 2x speed, but 4x is fairly straightforward because a lot of the time is spent creating match sets that already exist.

##### **Geohot** [[00:53:46](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3226)]
Do you have a working branch for this that passes tests?

##### **Ttomsa** [[00:53:53](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3233)]
No.
So one thing that's left is any source.
But I essentially remove just the single use from symbolic, which doesn't really affect the speed, because I'm just trying to measure the speed.
Any source depends.
The implementation of any source
And I guess also the permutations depend on how I do the name assignment.
Because right now, I just have to deduplicate, or I guess duplicate.
So if we have, for example, an add.

##### **Geohot** [[00:54:28](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3268)]
You just do all the permutations.

##### **Ttomsa** [[00:54:31](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3271)]
Yeah, because the name assignment needs to be a straight thing where we we can't have like more than one um possibility because then we we would have to match again 
i think it's possible to get 4x 

##### **Geohot** [[00:54:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3287)]
Great uh yeah this might be the uh you might be making the most money per line in tinygrad's history if it looks like the same sort of 60 line thing

##### **Ttomsa** [[00:54:58](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3298)]
I am really happy with the way it looks.
It's not going to look as nice, I guess.
There's a little bit more, because for the match set creation, I also check the binds.
I check if the variable bindings are valid or not.
And that's a couple more lines.
So yeah.
Also, I wanted to say 8x is definitely not possible.
I don't think it's possible anyways.
But with this approach, it's not possible, because just the time to actually do the lookups, the time to hash the tuples, that alone takes more than what would be an 8x speedup.

##### **Geohot** [[00:55:46](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3346)]
Yeah, I mean, 4x is not 4x.

##### **Ttomsa** [[00:55:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3347)]
And everything takes so long at these speeds.

##### **Geohot** [[00:55:51](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3351)]
4x is a great victory.
I think with some of the.. Maybe to get more speed beyond that, we'll have to rethink maybe what some.. I'm always open also to changing the spec a little bit.
If any turns out to be really slow, well, maybe we can't use it or we have to implement it in a different way.
But 4x is a huge victory.

##### **Ttomsa** [[00:56:14](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3374)]
I guess one suggestion is that currently any is essentially..
It just creates a pattern that's never checked.
Only the sources are checked.
And that does allow you to kind of nicely.. Essentially, any is the same as a permutation in the sense that any source is valid.
It's not done like a permutation.
It creates this extra sort of pattern.
And it would be nice if it didn't.
It would simplify stuff.
But I guess you can't then do..
the nice stuff that you can with any, where you can just have any in one of the sources.

##### **Geohot** [[00:56:51](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3411)]
I did this once where I replaced the permutation logic using any.
I was like, oh, this logic's in here twice, but it made everything way slower, so I had to revert it.
You're saying that the permutation's hard to support or any is hard to support?
Because the permutation is a subset of any.

##### **Ttomsa** [[00:57:17](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3437)]
No, it's just that, I guess I'm thinking about this, but any creates a pattern that is never actually checked, right?
It skips the check for itself and only checks its sources.
So if you look at the code, the way it checks for permutation, it just has an any, right?
And then inside of the any is the all.
But then you couldn't do that with UPat.any, right?

##### **Geohot** [[00:57:39](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3459)]
You could reimplement that however you want.
UPat.any is just a way that I wrote it to make the old matcher work.
You can totally change that logic that's in any.
to actually construct all the permutations of the pattern.
If you want to construct all the permutations of the pattern at any time, I'm totally fine with that.

##### **Ttomsa** [[00:57:57](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3477)]
Yeah, the only thing is that I had
*Internet problems*
But the thing is, upad.any does allow you to do some nice things.
For example, you can say that the first source is an any, and then the second source has to be something else.
And it will check, it will automatically do the, you know, for example, let's say that any is any of three.
The first one with the second one, the second one with the second one, and the third one with the first one, right?
You can't do that if you don't have that nice sort of..
formatting if you actually have to.. I don't know.
I guess I'll just.. 

##### **Chenyu** [[00:58:39](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3519)]
Is the case you just described used anywhere in TinyGrad now?

##### **Ttomsa** [[00:58:48](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3528)]
Yes, it is.
It is used.
It's used in the rewriter.
In Symbolic, it's used in that.

##### **Geohot** [[00:59:00](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3540)]
We use any rarely enough, so one thing we could do with any to replace it
I thought about even writing this when I was writing any is, but then I wrote that thing and it wasn't that slow.
Like if there's like, say there's like three anys inside of a pattern and those three any's each have two things.
I'm okay with basically just creating eight X eight rewrite rules, right?
Like, like the any is just syntactic sugar around creating all the possibilities of the any.

##### **Ttomsa** [[00:59:30](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3570)]
I'll think about it.
Cause it's, it's,
It's easy to fix, or it's easy to implement.
It just maybe looks a bit ugly.
I guess it's what I was thinking.
But I'll see how it looks, and then I guess I'll think about it more.
But I haven't actually implemented any, but it's not difficult.
It's just I delayed it because I just delayed those decisions because it's not really relevant for the speed measurement, which is what I'm sort of interested in.

##### **Geohot** [[00:59:56](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3596)]
Agreed.
Yeah.
Let's get tests passing, even if the any tests all fail.

##### **Ttomsa** [[01:00:02](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3602)]
Also, a couple of other things.
I think this is a small thing.
The top-down rewrite and the bottom-up rewrite, I think they should be switched, the names.
Because usually bottom-up means leaf to root, and top-down means root to leaf.
And they're switched, apparently.
It's kind of confusing, I guess.

##### **Geohot** [[01:00:23](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3623)]
Yeah, I mean, I always think of sinks as the bottom.
I don't think we should.
Because I understand that that's usually how it is in the other kind of, like a normal tree.
But the sink is at the bottom or on the right in this graph.
So bottom up is from the sink upward.
And top down is from things that feed into the sink.

##### **Ttomsa** [[01:00:47](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3647)]
If you print it, it prints the sink first, right?
Basically meaning..

##### **Geohot** [[01:00:51](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3651)]
The print is backwards, yes.
The print is backwards.
Take a look at it in Viz.
You'll see the sync on the right.

##### **Ttomsa** [[01:01:02](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3662)]
And also, is there a reason why the rewrite cache doesn't persist across kernel?
I did that, and it's a speedup, but it's not that substantial.

##### **Geohot** [[01:01:17](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3677)]
Yeah, let's not do that yet.
We'll get there.
So the two reasons we haven't done it yet.
One is any rewrite with a context, you can't do this.
So you're going to have to support non-cache rewrites anyway.
And two, I'm not sure what the memory implications are.
Like, what is the free policy on this cache?
Is it never free?
Is it LRU?
So..
Yeah, that's definitely another project that's, I wouldn't touch it for this, but I've certainly thought about it.
And like, yeah, like a whole lot of the rewrites in TinyGrad will affect, a whole lot of the caches in TinyGrad will effectively become the graph rewrite cache.
We have like the method cache, and the method cache could basically be a graph rewrite cache at some point.

##### **Chenyu** [[01:02:15](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3735)]
Anything else you want to add for graph rewrite?

##### **Ttomsa** [[01:02:20](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3740)]
No, that's it.

##### **Geohot** [[01:02:24](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3744)]
Great, yeah.
Looking forward to seeing it pass the tests.

##### **Chenyu** [[01:02:28](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3748)]
Yeah.
I think I, is there other active bounties that I'm missing?
I think that's it.

##### **Geohot** [[01:02:44](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3764)]
Oh, T1G isn't here, but there's the LLVM backend bounty that's being worked on.
That's pretty cool.

##### **Geohot** [[01:03:00](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3780)]
Yeah, we can remove co-manager, and then that officially removes every piece of AMD software from our stack.
Our driver is not AMD.
Our compiler is just LLVM.
It'll be just LLVM.
It's normal LLVM 19 upstream.
So sure, AMD might have still wrote the code, but it's upstream LLVM.

##### **Chenyu** [[01:03:22](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3802)]
Great.
Yeah, that's nice.
OK, I think that concludes the meeting.
Thank you, everyone, and see you next week.

##### **Geohot** [[01:03:40](https://www.youtube.com/watch?v=m7zQq40dr2M&t=3820)]
Bye~
