# 2025-02-03 Meeting

### Meeting Agenda

**Time:** 6:00 AM San Diego time (PST) or 10pm Hong Kong time
- company updates
- new llvm, dsp
- scheduler
- mlperf resnet, bert
- Ops.POW, rand_like
- drivers
- tensor cores
- webgpu, tinychat
- bounties (onnx, retinanet, graph rewrite 2.0, sorting add chain)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=0)

### Highlights

- [Tinybox Reds](#geohot-000005) We have 6 tinybox reds in stock, please buy reds. (5090 boxes soon)
- [Need for Speed](#geohot-000323) Geohot is interested in paying out bounties that improve SPEED!
- Everything else is moving along, DSP, scheduler, mlperf, tensorcores, etc.
- [Graph rewirte](#geohot-004638) Geohot: "if no one does it by March, I'll start taking it seriously."
- [Closing remarks](#geohot-005136) From Chenyu and Geohot on how great projects take time

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=0)]  
Any company update?  

##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=5)]  
We're getting a lot of inquiries.  
We even got someone who found the dead pre-order link for TinyBox Pros and tried to pre-order two of them.  
I cancelled the pre-orders because there's no way we're getting more 4090s.  
We have 12 5090s coming.  
We're working on the TinyBox 2 green, which is going to be 4 5090s in a box.  
4 5090s because you can't really power sticks.  
And they're also super expensive.  
It's looking like they're going to cost us $2,600.  
Uh, but like, you know, what am I going to say?  
Like, that just seems to be the price to buy these things in bulk.  
Uh, so, you know, I'm not, you'll guys will see what we charge.  
It's, it's not, it's not, I'm paying more than retail to get a lot of them, which is kind of awful, but I mean, you know, they work it out.  
They're like, well, okay.  
They're 2,400 retail.  
You could hire runners to go around to best buys around the country and buy up 5090s, but it's not worth it.  
Just pay us 2,600.  
So, yeah, we're working on getting them.  
That's the biggest thing.  
We're also working on a rainbow tiny box just for internal use.  
And we have six reds in stock.  
So someone buy reds, please.  
Please buy tiny box reds.  
We have lots of tiny box reds.  

##### **Chenyu** [[00:01:35](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=95)]  
Great.  
Okay.  
Next one is also for you.  
Can you talk about the new LLVM?  
You have the most experience with that and also the DSP.  

##### **Geohot** [[00:01:52](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=112)]  
Yes, so we merged LLVM Bounty for new LLVM.  
New LLVM switches away from LLVM Lite and just talks directly to the library.  
And yeah, I mean, it's a bit more lines, but it's nice to remove the LLVM Lite dependency.  
Yeah, it also uses the ClangJit CPU program, which is... I see a way that we can unify LLVM and Clang into one CPU backend, so they could share buffers, and they're just different.  
Clang and LLVM are now a lot more like CUDA and PTX.  
Cuda and PTX have the same runtime, but different compilers.  
So we could do the same thing with LLVM and Clang.  
And then also, this is a way that we can unify CPU program.  
I see a way that this can become multithreaded, which is nice.  
So yeah, we could build a GPU-ish runtime environment for multithreading CPU stuff.  
But yeah, it's basically just LLVM light removed and a switch to CPU program instead of the MCJIT, our own form of MCJIT.  

##### **Chenyu** [[00:03:14](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=194)]  
Do you want to add new bounties along that direction for LLVM or CPU program?  

##### **Geohot** [[00:03:23](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=203)]  
I don't think it would work.  
stuff requires a lot of taste to do it right uh i think that yeah we're not there yet we're not ready to write this yet uh but yeah no it's just kind of gonna look like a refactor i'm not really sure what we can bounty there although i am interested i mean the thing that i really want to figure out how to bounty and i think it should be doable is speed  
If people can get things to be faster, I'm interested in paying out bounties for that.  
And then figure out how to get things faster.  
If you can add a new trick, that's what I really want.  
I mean, we're going to have to deal with... I guess I'll talk about the DSP a little too and the tricks that are going to be required.  
So the first thing that I'm working on is a DSP emulator.  
I have that working.  
So I'll get that merged tomorrow.  
We'll have some CI tests for the DSP, which would be nice.  
And then I can start working on what...  
I don't think LLVM client actively uses SIMD.  
They definitely use SIMD.  
They definitely, LLVM opt will definitely enable SIMD.  
And CPU performance is certainly a priority, right?  
Our goal is to be performing on every piece of hardware and there's only so many track.  
So the DSP basically has three tricks that we're gonna figure out how to have to use.  
One is just SIMD instructions, which is just vectorized math.  
Another is the DSP has what's called tightly coupled memory.  
It's like eight megs of SRAM that you can read and write from very quickly.  
And then there's also the large registers.  
So there's registers like memory can be coalesced beyond the compute, and then you can do something like shift the register, which is a very cheap operation.  
So basically those three things, this is what I'm going to be working on probably for the rest of the month.  
And hopefully we can finish the DSP bounty, the DSP bounty for us, the DSP contract a month ahead of schedule.  

##### **Chenyu** [[00:05:42](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=342)]  
Cool.  
Sounds good.  
Anything else you want to add before we move on to the next item?  

##### **Geohot** [[00:05:51](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=351)]  
You know, maybe... Okay, so there aren't any SIMD instructions while debugging LLVM and ClangJit.  
I mean, I want to... There's some way I could... Maybe propose... UUVM, maybe propose a bounty that will capture what I'm trying to get at with this CPU speed.  
Like, I think if...  
It's a little bit annoying on Mac because Mac Torch CPU uses AMX, but I'd really like to be beating Torch CPU.  
How about we can do it on the CI machines?  
Beat Torch CPU on the CI machines for like some common models.  
I don't care if it's LLVM or Clang, but we have like a CPU backend and I want to beat Torch on the CI machines.  
so yeah let's see let's like think about what let's think about what model we want to do.  

##### **Chenyu** [[00:06:52](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=412)]  
Llama llama everyone wants llama everyone wants llama   

##### **Geohot** [[00:06:59](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=419)]  
yeah that seems good okay cool $500 bounty yeah well what's the smallest llama now  

##### **Chenyu** [[00:07:11](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=431)]  
I think there's like 1B, the one we use in chat.  
The small one we use in chat, not a default one.  

##### **Geohot** [[00:07:23](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=443)]  
Is the small one we use in chat a llama?  

##### **Chenyu** [[00:07:29](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=449)]  
Not a llama?  
It's a K6 quantized llama, right?  
That one.  
Anyway, the smallest llama.  

##### **Geohot** [[00:07:41](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=461)]  
Well, let me... Yeah, yeah, yeah.  

##### **Chenyu** [[00:07:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=465)]  
Or GPT-2.  

##### **Geohot** [[00:07:46](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=466)]  
Yeah, yeah, yeah.  
No, let's stick with Llama 1B.  
So Llama 1B faster than Torch on CPU in CI.  
No weight download needed.  
Just model speed.  
Cool.  
either LLVM or Clang fine.  
Great.  

##### **Chenyu** [[00:08:30](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=510)]  
OK, let's move on to scheduler.  
I saw many discussions.  
Oh, George, you want to talk again?  
It's Qazalin is just listening.  

##### **Geohot** [[00:08:42](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=522)]  
Yeah, no, I think I put together some good stuff this morning.  
Just kind of like Qazalin is doing a lot of refactors that are like getting it to the point where we can actually do this.  
So this morning I wrote a... a scedule sync.  
So what schedule is going to become is it's just going to become a becomes map.  
And then the scheduler will basically assign a kernel to the buffer.  
And then the tensor will become an assign buffer and kernel.  
And that kernel will point back either to assigns or buffers also.  
and that'll be scheduled.  
And then realize is where we'll do like the actual scheduling in terms of linearization.  
So scheduling means two things.  
It means grouping and linearization.  
This will really separate those two things and scheduling will just be the grouping.  
There's grouping and there's also compilation.  
There's grouping, compilation and linearization.  
Yeah, I mean, you can see, I think the best way to describe any of this is to just look at that last picture that I posted in scheduler.  
which is just, like, you can see kernels, buffers, and assigns.  
Yeah, so my PR is passing tests, but it's not written in a, it's just, I just, like, shoved it after the old scheduler.  
So, yeah, I think.  

##### **Chenyu** [[00:10:11](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=611)]  
So an assign can point to another assign.  

##### **Geohot** [[00:10:16](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=616)]  
A sign can point to another sign, yes.  
You can stack a sign.  
So the buffer inputs...   

##### **Chenyu** [[00:10:20](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=620)]  
Oh, that's versioning.  

##### **Geohot** [[00:10:21](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=621)]  
It's versioning, yes.  
And I believe that I got the toposort right.  
So I have a toposort that adds extra edges to enforce the versioning.  
Yeah, so I think I'm happy with it.  
I think the toposort of right, but I think it's just the graph construction.  
So that's what we were going back and forth about.  
We have to figure out how to do the graph construction without doing BFS.  
But I think that's totally doable.  

##### **Chenyu** [[00:10:51](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=651)]  
OK.  
Well, that's exciting.  
Graph construction is a challenge.  
Great.  

##### **Geohot** [[00:11:00](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=660)]  
Yeah, it shouldn't do the BFS.  
Yeah, it's going to be a challenge to get those things exactly right.  
But I think at the end, you'll be much happier than things like preloads and pre-schedule and stuff.  

##### **Chenyu** [[00:11:10](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=670)]  
Yeah, preload is sketchy and adds other limitation to assign.  
So exciting.  
Great.  
It shouldn't do that BFS.  
OK.  
Qazalin if you want to add anything, you can just type.  
Otherwise, I'm going to move on to the next stuff.  
So MLPerf, ResNet, I have been trying to debug this for a week.  
So my current conclusion is I think our ResNet was not less stable even before the new multi and new gradient change.  
my impression is if we use more tensor cores or if we use float as dtype then the numeric is much better and if not there can be like very small diff so my conclusion now is because the  
Kernels are grouped slightly differently now.  
We do tensor cores slightly differently.  
That's why we see a little bit of numerical loss.  
It's very possible that we can tune the hyperparameters again so that it converges again, but I don't feel like that's a top priority now.  
I match every possible source of bugs I can think of, and I didn't really find anything.  
And also, prior to the new multi and gradient change, if we disable tensor cores, or if we use float, or we use Winograd, none of those really converge.  
So my belief is our hyperparameter was overfit to that setting, and it's never less stable.  

##### **Geohot** [[00:13:08](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=788)]  
Yeah, makes sense.  

##### **Chenyu** [[00:13:12](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=792)]  
Yeah, so that's a little bit annoying.  
I'm pretty sure if we increase the epoch and the one op, we can probably find another thing that also converges.  
I just don't think it's worth it, given that we are going to change scheduler again, and overfitting this really doesn't help.  

##### **Geohot** [[00:13:30](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=810)]  
No, I definitely agree that overfitting doesn't help, but we have to find some way to deal with, like, where is this numerical instability coming from and how do we debug things like that?  

##### **Chenyu** [[00:13:39](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=819)]  
Yeah, so I think we can talk about that in the later Tensor Core stuff.  
I think this is definitely... Oh, sorry, go ahead.  

##### **Geohot** [[00:13:50](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=830)]  
Is it good with float32?  

##### **Chenyu** [[00:13:52](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=832)]  
No, but our ResNet was also not good with float32.  

##### **Geohot** [[00:13:57](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=837)]  
Oh, yeah, no, see, that's much more concerning to me.  

##### **Chenyu** [[00:14:01](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=841)]  
Yeah, so that's why I believe it's none of these stuff, and it's just the numerics.  

##### **Geohot** [[00:14:08](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=848)]  
Yeah, but if it's numerically unstable, like float16 is not numerically stable, but if float32 isn't working, we have something that's really like a bug.  

##### **Chenyu** [[00:14:18](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=858)]  
I think using tensor cores is better numerics, and there's no float32 tensor core.  
So all those reduced loops much worse compared to Tensor Core in terms of numerics.  
That's my belief.  
So bfloat16 was converging.  

##### **Geohot** [[00:14:43](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=883)]  
I see.  
But also, why do we have worse numerics if we're not using Tensor Core?  

##### **Chenyu** [[00:14:50](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=890)]  
I think it's just the ...  
I am not too sure, but my belief is because we do accumulate on ACC, right?  
And the problem is if that ACC becomes too big or too small into a negatives, then your additional add might be canceled.  

##### **Geohot** [[00:15:09](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=909)]  
How did TensorFlow course fix this?  

##### **Chenyu** [[00:15:12](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=912)]  
Because TensorFlow course kind of adds add eight together and add that to our ACC.  

##### **Geohot** [[00:15:19](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=919)]  
But we can emulate that.  

##### **Chenyu** [[00:15:21](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=921)]  
Yes, yes.  
We also previously know if we apply no op-opt or no reshape to let no enrolling, enrolling is much better, numerical-wise.  
I don't have a good framework to describe this, but I think that might be the source of issue here.  

##### **Geohot** [[00:15:46](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=946)]  
I'm very interested in a framework to describe this.  
If this is a real thing, like I've always wondered like how much better deep learning could be if this stuff worked.  

##### **Chenyu** [[00:16:01](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=961)]  
Which stuff?  

##### **Geohot** [[00:16:02](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=962)]  
Just in general, like how many things in Torch are numerically unstable?  
I've had problems.  
Oh, I've had, I mean, this is not a tinygrad specific problem.  
I've had tons of problems in other frameworks like this too.  

##### **Chenyu** [[00:16:27](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=987)]  
Yeah, so something to think about.  
I don't have a good solution now.  
And I don't think it's any of those unsync bachnorm change or gradient change.  
I think those looks fine.  
It's just things are looping slightly differently now.  

##### **Geohot** [[00:16:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1005)]  
Yeah.  

##### **Chenyu** [[00:16:46](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1006)]  
So that was the conclusion.  
I'm also interested to see how we quantify or make numerics better.  
OK, so BERT is the thing I will talk next.  
We don't have DROPOUT now.  
For some reason, it converges better without dropout.  
I'm not sure why.  
Maybe we have a bug in dropout or something.  
But since we don't have dropout, we cannot really talk about performance.  
And also because we removed multi, I think.  
I think we removed multi and used more memory.  
So we can also not fit the current BERT batch size.  
I think the improvement to BERT, those kernel groupings thing would live in the new world after we have the new scheduler.  
So that's why I'm excited about the grouper change.  

##### **Geohot** [[00:17:49](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1069)]  
What do you mean by a new scheduler?  

##### **Chenyu** [[00:17:52](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1072)]  
No, the grouping framework.  

##### **Geohot** [[00:17:57](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1077)]  
Yeah.  

##### **Chenyu** [[00:17:58](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1078)]  
Can I go and do the multi reduce back to back now?  
Or can I go and do the fuse Arange now?  
Or should I wait?  

##### **Geohot** [[00:18:10](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1090)]  
It is a dream.  
Yeah.  
I mean, I want to definitely get this kernel stuff done first.  
Because then we could at least see what's going on.  
It's becoming more readable.  
The scheduler is definitely a lot better than it was a few weeks ago.  
But yeah, maybe it's still hard to do these things.  
But I don't understand how this affected the memory for multi.  

##### **Chenyu** [[00:18:53](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1133)]  
I thought we had more kernels now.  

##### **Geohot** [[00:18:57](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1137)]  
Oh, this might all be cast before view stuff.  

##### **Chenyu** [[00:19:04](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1144)]  
Not really.  
I test after removing cast before view.  

##### **Geohot** [[00:19:10](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1150)]  
And I'm not really sure what else changed.  
But if you see that thing, the cast before view thing is really just, it all comes down to when you realize expands and when you don't.  

##### **Chenyu** [[00:19:21](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1161)]  
Yeah.  
Yeah, I have a test PR on that, but that saves memory sometimes and disable tensor cores in other times, because now you merge other things that tensor cores op-op doesn't allow.  
That's a bug in the op-opt of tensor core.  
As it stands, it's not necessarily better.  

##### **Geohot** [[00:19:53](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1193)]  
Wait, I don't understand.  
There's a bug in the op-op of tensor cores?  

##### **Chenyu** [[00:19:58](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1198)]  
So current TensorCore op-opt only triggers TensorCore if it's from a load or from our cast after load.  
If you add more stuff before last step, it doesn't trigger TensorCore.  
TensorCore should just be a reduce, right?  
Not concerning about the ALU before that.  

##### **Geohot** [[00:20:22](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1222)]  
Well, no.  
It's a mul and a reduce.  

##### **Chenyu** [[00:20:25](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1225)]  
Yeah, the mul and a Reduce.  

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1229)]  
Yeah, I mean, the Tensor Core stuff has still got a lot of old-fashioned code that needs to be rewritten as rewrite rules.  
I'm not sure who's going to do that.  

##### **Chenyu** [[00:20:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1245)]  
Let's see.  
OK, so let's ResNet and BERT.  
I also add ops.pow because we want pow.  
And I wrote a new gradient for pow, and that's very short.  
So I'm pretty happy.  
It currently works on some backends that's easy to implement pow in the render.  
I think for CLANG and LLVM,  
We either need transcendental style stuff, or I think there's a way to call this.  
So looking to that.  

##### **Geohot** [[00:21:35](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1295)]  
Wait.  
We definitely need transcendental style stuff.  
OK.  

##### **Chenyu** [[00:21:39](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1299)]  
Then find a way to write transcendental for pow.  

##### **Geohot** [[00:21:44](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1304)]  
But can't you just use what used to be in Tensor?  
It used to be in Tensor.py?  

##### **Chenyu** [[00:21:52](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1312)]  
I don't know if that's correct, because previously we had some issues in back-end, but maybe forward and just copy that should be fine.  

##### **Geohot** [[00:22:01](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1321)]  
I think, yeah.  
I think just forward and copy that should totally be fine.  
And then it's like Transcendental style.  
It's just that.  
Just do a rewrite if the back-end doesn't support pow.  

##### **Chenyu** [[00:22:14](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1334)]  
OK, that sounds good.  

##### **Geohot** [[00:22:16](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1336)]  
We may also prefer that on GPUs, because GPUs don't have pow instructions.  
Like, yeah, I don't think we actually want to use, like, if the renderer has a pow, I don't think we want to use that.  
I think you probably always want to do the rewrite.  

##### **Chenyu** [[00:22:40](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1360)]  
I mean, this we can benchmark after we have the transcendental, right?  
Yeah, sure.  
Only GPU and metal can call the pow.  
I don't know what that calls into.  

##### **Geohot** [[00:22:52](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1372)]  
It's not real.  
It's not real.  
It just generates tons of crappy GPU code.  

##### **Chenyu** [[00:22:56](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1376)]  
OK, great.  
Yeah, so that's pow.  
And also, after that, I would fix the integer again.  
I disabled old integer.  
It was not correct anyway, and it was blocking some other stuff.  
rand-like.  
Or similarly, ones-like, or anything that depends on the like, that you're, I think, it almost feels like you want to, you UOp for that, which, and the source is the thing you want to be like to, that you resolve after that.  

##### **Geohot** [[00:23:40](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1420)]  
No, I don't think you want to do that.  

##### **Chenyu** [[00:23:44](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1424)]  
But then how?  
locally how to know what it would look like.  

##### **Geohot** [[00:23:51](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1431)]  
You mean access for multi?  
We just need to move that logic into ops and have it just recursively compute it.  

##### **Chenyu** [[00:24:01](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1441)]  
Oh, so like device.  

##### **Geohot** [[00:24:04](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1444)]  
Yeah, you definitely don't want to, like device, yeah, you definitely don't want to start adding, like, pow is fine, but adding UOPs is bad.  
Like, we need to delete a lot of UOPs.  

##### **Chenyu** [[00:24:17](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1457)]  
Okay.  

##### **Geohot** [[00:24:18](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1458)]  
Right, because you could imagine a world where someone eventually is like, well, why don't we just have a conv UOP?  

##### **Chenyu** [[00:24:24](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1464)]  
Yes.  
Let's have an Arange UOP.  
I want an Arange UOP.  

##### **Geohot** [[00:24:28](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1468)]  
An Arange UOP, yeah.  

##### **Chenyu** [[00:24:32](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1472)]  
Yeah, OK.  
OK, I will think about that.  
We can definitely do a device-like style to propagate the axis in the lazy fashion.  

##### **Geohot** [[00:24:42](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1482)]  
Yeah, let's start right there.  

##### **Chenyu** [[00:24:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1485)]  
OK, I will think about Arange.  
So another thing is, I think Arange, specifically for BERT, because we cannot do the compute on device, we need to create one big Arange, then copy that to  
individual device that wastes memory.  
But I don't have a good idea yet to think about that.  
Definitely not Arange UOp.  

##### **Geohot** [[00:25:17](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1517)]  
We're getting closer to being able to write that in the scheduler.  
So we have this thing, tensor map.  
We're getting closer to be able to add rewrite rules there that will do this stuff nicely.  

##### **Chenyu** [[00:25:31](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1531)]  
So the problem is kind of you don't really know Arange is let in a much later rewrite rule because the Arange rewrite rule is in rewrite.  

##### **Geohot** [[00:25:51](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1551)]  
Wait.  
Oh, no, that doesn't matter.  
A range while it's in the scheduler is just a reduce on a const.  
And a reduce on a const should trivially have all devices just shoved through it.  

##### **Chenyu** [[00:26:07](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1567)]  
But then how do you know your reduce on a const can be independently compute on each device?  

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1577)]  
Of course it can.  
It's a reduce on a const.  

##### **Chenyu** [[00:26:24](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1584)]  
Oh, okay.  
Yeah, you're right.  

##### **Geohot** [[00:26:27](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1587)]  
Right.  
Every, every, yeah, no, this is a much simpler rewrite rule than the, than the fancy arange folding stuff.  

##### **Chenyu** [[00:26:34](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1594)]  
Well, I was thinking about you do a reduce on the arange again.  
Okay.  

##### **Geohot** [[00:26:40](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1600)]  
Yeah.  
No, not at that level.  
I just look at this in viz.  
I think it might actually be really simple now.  

##### **SPEAKER_03** [[00:26:47](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1607)]  
Okay.  
Oh, sounds good.  
Okay.  
I will look into that too.  

##### **Geohot** [[00:26:56](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1616)]  
Yeah, I mean, anything.  
So what I'm imagining it's doing is, like, creating this.  
So it's got, like, a const reduce, and then it's got some shard, right?  
And you could totally just shove that.  

##### **Chenyu** [[00:27:11](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1631)]  
You could shard that on the const, and you reshuffle, so the reduce after you apply the multi thing to the const.  

##### **Geohot** [[00:27:20](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1640)]  
Yeah, you might even be able to put this in multi.  

##### **Chenyu** [[00:27:30](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1650)]  
Basically, you realize your const can be split into a multi of const that's smaller.  
And you have the shape there, and you apply the reduce to that.  
And if it's even better, wait.  
OK, you still need to figure out your offset for every device.  

##### **Geohot** [[00:27:59](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1679)]  
I mean, you need to basically shove the thing.  
Yeah, you need to reshuffle the views with the other stuff.  

##### **Chenyu** [[00:28:05](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1685)]  
No, no, no.  
But for Arange, say the first element of your Arange on every device depends on which device you are, right?  
So for the first device, this is zero.  
For the second one is how many consts there were before your device number.  

##### **Geohot** [[00:28:22](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1702)]  
Yeah.  
But that just expresses itself as a view.  

##### **Chenyu** [[00:28:30](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1710)]  
Why is that a view?  

##### **Geohot** [[00:28:31](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1711)]  
It's a view.  
It's just like a slice, right?  

##### **Chenyu** [[00:28:39](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1719)]  
But OK, I will think about this more.  
I think there are some details that I'm not so sure.  

##### **Geohot** [[00:28:46](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1726)]  
Post the pattern in Viz.  
Look at the pattern in Viz and post it, and then we can talk about it.  

##### **Chenyu** [[00:28:53](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1733)]  
Yeah, that sounds good.  
OK.  

##### **Geohot** [[00:28:54](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1734)]  
I'm curious now what it is.  

##### **Chenyu** [[00:28:58](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1738)]  
No, exciting stuff.  
Great.  
Let's move on to drivers.  

##### **Nimlgen** [[00:29:08](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1748)]  
Yeah, so I've been working mostly on the AM access and pausing stuff.  
So I'll continue to do this P Suite as well.  
And it's a good work, and I believe P is big.  
But it's still mostly a sense of like SCSI Commons.  
So yeah, I'm just now looking into the firmware to find a better way to access this.  
So yeah.  

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1782)]  
I think the bigger advantage to libUSB, I didn't expect to get any more perf.  
I just expected it to work mac.  

##### **Chenyu** [[00:30:00](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1800)]  
Nimlgen, I think you're not here.  

##### **Nimlgen** [[00:30:08](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1808)]  
Yeah, I mean, I had some connection problems.  

##### **Chenyu** [[00:30:12](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1812)]  
Oh, OK.  
So I'm not sure if you are talking.  
But if you have connection problem, you can also just post in the channel.  

##### **Nimlgen** [[00:30:35](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1835)]  
Are there any questions?  
Maybe I missed something.  

##### **Chenyu** [[00:30:41](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1841)]  
It's just you have a background noise.  

##### **Nimlgen** [[00:30:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1845)]  
Yeah.  
OK.  
Sorry.  
Sorry about that.  
No worries.  

##### **Geohot** [[00:30:53](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1853)]  
But yeah, okay.  
So I see from your post, yeah, I'm interested to see what's different between the 24 and the 23.  
I bet they just moved a bunch of commands around.  
Fundamentally, we're going to have to figure out how to use the fast AMA stuff.  

##### **Nimlgen** [[00:31:19](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1879)]  
Yeah.  

##### **Chenyu** [[00:31:30](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1890)]  
Only hear you say yeah, but OK.  
OK, if you have anything else to comment, you can just post in the channel.  
And we are going to move on to TensorCores.  

##### **Ignaciosica** [[00:31:46](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1906)]  
Hi, hello.  
Search over a tensor core shape in each initial benchmarking gives hints that it is lower for smaller beam, as it tends to find local minimum with smaller shapes.  
Though this might be a problem on the search algorithm rather than on the searching over the shape itself.  
I think we might want to add this, but under a disabled flag, at least until the search algo gives better results, or only enable it if the beam count is high enough to overpass this local minimum.  

##### **Chenyu** [[00:32:32](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=1952)]  
I see.  
Yeah, I think for your PR, it's probably good enough to include some examples.  
So my comment was to, I just want to see there are some examples that really pick these actions to making sure it's correct.  
If you think better to gate this,  
depends on BEAM number or something.  
I mean, unless it's making things drastically slower, I think it's probably fine to leave it as is.  
Our search algorithm is not good with tensor cores anyway.  
So don't worry too much on that.  

##### **Ignaciosica** [[00:33:21](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2001)]  
Yes, I would flag it under a BEAM count.  
or flag directly because it gives a smaller worst performance.  
Consider it was worst performance for some shapes if the beam is free or edge or something like that.  

##### **Chenyu** [[00:33:42](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2022)]  
OK, sure.  
No problem.  
So my point was I want to see some examples that really pick these new answer cores and making sure it's correct.  
Yes, OK.  
Otherwise, the default setting, I will use whatever you recommend.  
You are more experienced in running that.  

##### **Ignaciosica** [[00:34:01](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2041)]  
OK, thank you.  
I also added accumulation on half for Tensor Cores for NVIDIA and PTX.  
It's the PR open.  
I don't add it.  
And I also fixed an annoying bug.  
And for the numerical stability framework, as well as for the five-gen TensorCore, I started studying.  
So no update from my side.  
And from what you mentioned in this meeting, I can focus on the rewriting the TensorCore's old-fashioned code if you think it's a priority.  
Otherwise, I'll continue working on the things I mentioned above.  

##### **Geohot** [[00:34:42](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2082)]  
Well, I'm really interested in the framework of numerical stability.  
I'm really interested in a way to just start discussing numerical stability and saying, OK, what's actually going on here?  

##### **Ignaciosica** [[00:34:55](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2095)]  
OK.  
Yeah.  

##### **Chenyu** [[00:35:00](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2100)]  
A lot of these, enrolling more is more precise, or using Tensor Core more is more precise is anecdotal.  
And it would be nice to have a way to discuss things like this.  
Maybe there are some terms or papers that I'm pretty sure people have studied this before.  
And it would be good to have some terms and ideas to thinking about a problem.  

##### **Ignaciosica** [[00:35:29](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2129)]  
Yes.  
Yes, I agree.  
Though it might take an extensive research from my side, so don't expect rapid progress.  

##### **Chenyu** [[00:35:41](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2141)]  
No worries.  
If you find anything interesting, just post in the channels.  
I can also take a look.  

##### **Ignaciosica** [[00:35:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2145)]  
Sure.  

##### **Ignaciosica** [[00:35:51](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2151)]  
Cool.  
Thank you.  
Let's move on to WebGPU and TinyChat browser.  
So Wpmed said, I think the PR is close.  
Use some more lines.  
And last time I read it, I think some of the functions thing can be cleaned up a bit.  

##### **Geohot** [[00:36:16](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2176)]  
Yeah, I still think there's a bunch more cleanups to do on it.  
I raised the bounty to $400.  
It's plus like 100-something lines, and I don't think it has to be.  
Yeah, so I think just that.  
I gave a list of things on that pull request.  
But yeah, we'll talk about it.  

##### **Chenyu** [[00:36:48](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2208)]  
Oh, great.  
It's always nice to remove more dependencies.  

##### **Geohot** [[00:36:54](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2214)]  
Yeah, it's good to use Dawn as well.  
I mean, it's the real one in Chrome.  
I double checked this.  
I looked, I'm like, I don't just want to switch to some other library.  
But if we're switching to the one that is in the older web browser anybody uses, sure.  

##### **Chenyu** [[00:37:06](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2226)]  
Yeah.  
OK.  
This is good.  
How about a tiny chat in browser?  
You should be a speaker if you want to talk about it.  
You don't have to.  
Don't mute it.  
I think that's on you.  
I mean, you ever heard the speaker role?  

##### **Hooved** [[00:37:53](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2273)]  
Yeah, my bad.  
Yeah, so I don't have that much to say beyond my PR message that I posted on Friday.  
Concerning that, you know, hopefully within a day or so, I want to get it working on my iPhone 15 because that's the only phone I have to test.  
And, you know, maybe we could test on some other phones and chat, but  
just dealing with some bottlenecks on the phone that I wrote about.  
Concerning the float 16 support from the other PR, that's exciting.  
And we can enable that in tiny chat after it's merged.  
It might take a little development just to get it in there.  
Not everyone's going to have that flag enabled in their browser.  
still have to account for that.  
But I think we can include that.  

##### **Geohot** [[00:38:51](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2331)]  
Yeah, I'm less worried about making float16 work.  
Is the model being cached?  
Right now when I go back to it, it's redownloading the model.  

##### **Hooved** [[00:39:00](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2340)]  
That's interesting.  
It should be cached.  
I can do some testing there.  
I mean, it is for me.  
might depend on your platform.  
Different platforms have different policies for indexed DB caching.  

##### **Geohot** [[00:39:15](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2355)]  
The stable diffusion caches work.  
This is Chromium on my Mac.  

##### **Hooved** [[00:39:21](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2361)]  
OK.  
Yeah, I can look into that.  
I do have a Mac that I could probably use for testing.  

##### **Geohot** [[00:39:29](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2369)]  
Well, I'll double-check, too.  
I just went to it right now, and I saw it.  
I saw its downloading model.  
My internet here is kind of slow, so it's moving, but slow.  

##### **Geohot** [[00:39:41](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2381)]  
I can also test later.  

##### **Geohot** [[00:39:52](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2392)]  
Cool.  
And you're waiting for iPhone before you want to start posting this link places and getting feedback and...  

##### **Hooved** [[00:39:57](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2397)]  
Yeah, just because I only use X on my phone.  
I bet a lot of people do too.  
So if someone sees a tweet and they click on it, I want it to be great if it just worked on the phone.  
Unfortunately, I found that there's some really tough constraints for playing on the phone.  
So I'm thinking if someone clicks on it on their phone,  
I'll just have, and if they don't have WebGPU enabled, I'll just have a link they can click to tell them how to enable WebGPU, and then reload the page, and then it'll work.  
Because Clang won't work on phones, I'm pretty sure.  

##### **Geohot** [[00:40:44](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2444)]  
Why not?  

##### **Hooved** [[00:40/graph:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2445)]  
OK, so yeah, I posted on there.  

##### **Geohot** [[00:40:47](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2447)]  
I saw the stuff about the, yeah.  

##### **Hooved** [[00:40:50](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2450)]  
I think we can make it work.  
It's just like right now, it's just I can't allocate one gigabyte byte array, a JavaScript heap array on my browser based on my tests.  
And that's the main bottleneck is just the token embeddings when they're not quantized.  
And when they're in float 32, it's one gigabyte.  
If we shrink it down, we can get it down.  
We can quantize it to something, and it'll work.  
We'd have to modify the Llama inference code, because that's not implemented in there yet.  
But I'm sure we could do it.  
I don't know what the speed cost would be.  
But yeah, it's all doing.  

##### **Geohot** [[00:41:38](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2498)]  
The token embedding alone is that large?  

##### **Hooved** [[00:41:41](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2501)]  
Yeah, yeah.  
The token embedding in float32 is one gigabyte.  

##### **Geohot** [[00:41:47](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2507)]  
whoa okay i didn't realize that yeah i thought you i thought this was just like the whole trying to load the whole thing into one thing and i'm like can't you break it up by tensor but   
uh yeah we'd have to kind of uh does the i mean this is kind of on the tinygrad side but does quantization work  

##### **Hooved** [[00:42:15](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2535)]  
I mean, I've quantized everything else.  
Well, not everything, but the stuff, all the linears in the transformer blocks, because that was already supported out of the box in master branch code.  
I haven't, I mean, to be clear, where I think Chenyu mentioned before, I'm using Q6K quantized weights and then unpacking them.  
for the token embeddings.  
So they can be quantized.  
It's just a matter of actually implementing it.  
If we were to, for instance, instead have that just be quantized, I'm sure we can make it work.  
I just don't know if there's going to be a big speed cost.  
I mean, it's probably fine.  
It'll just take some development time.  

##### **Geohot** [[00:43:12](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2592)]  
Yeah, I think this is outside the scope of the bounty.  
I'm happy.  
If you get it running on a phone in any way, shape, or form, I'm happy with that.  
Just something for the future.  

##### **Hooved** [[00:43:24](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2604)]  
Yeah, one last comment on that.  
Yeah, so that's what I'll do, just targeting WebGPU.  
The main reason I don't want to really do that right now is it's not so much because I don't think it can be done.  
It's just more the clang speed isn't that fast.  
So like,  
If someone uses it, I want them to not have a bad opinion about the speed.  

##### **Geohot** [[00:43:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2625)]  
Yeah, that's reasonable.  
We added a $500 bounty for speed.  
Someone can get CI llama to be fast.  
Cool, yeah.  
Let's focus on WebGPU then.  
Thanks.  

##### **Chenyu** [[00:44:06](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2652)]  
OK, let's move on to other bounties.  
Onyx, comment on the PR to merge ONNX files, I think is fine.  
But please do that in separate PRs, just one for simple copy and the subsequent ones for real change.  
That's a lot easier to review.  
RetinaNet.  

##### **Flata** [[00:44:35](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2675)]  
Hey, guys.  
Um, so for, uh, for writing that, um, I've been, I'm getting been bugged with the, uh, with this issue related to the, uh, the data loader test that I've written for it.  
Um, because it's kind of lazy sometimes when I, let's say merged it into master and all that, um, I try to narrow it down further.  
see what the issue is um but right now it seems to be stable but i think it's with the uh with the parallel testing on pytest on ci is probably causing the issue but um i'll take a look into it a little bit later just because i want to get into the into the training phase and for the validation one i've uh i re-ran the the validation data loader because i recently implemented that  
and made sure that it matches the metric, just using the pre-trained model so that it works.  
And they did verify that it works.  
So I'm actually just going to start the full training hopefully this week.  

##### **Chenyu** [[00:45:34](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2734)]  
Great.  
Oh, and just remember, I forget to reply to your message.  
Next time, just post in the channel.  
I don't read DM that much, or I read it and I forget to reply.  
Yeah, and I think we discussed in the PR about using multi-GPU for eval.  
And apparently, the bottleneck is not on that.  
So I think it's much better to figure out what it is before scaling to multiple GPU.  

##### **Flata** [[00:46:07](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2767)]  
Oh, yes.  
Yes, that's right.  
Thanks for that comment.  
Yes, I will take a look into that as well, actually, before I do the full training so that we don't waste time evaluating as if it was just one batch size, because it's similar speed anyway, for some reason.  

##### **Chenyu** [[00:46:23](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2783)]  
That's good.  
Graph Rewrite 2.0?  
We don't have the author here.  
I don't see any real progress there.  

##### **Geohot** [[00:46:38](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2798)]  
Yeah, I haven't seen progress there.  
I almost feel like Graph Rewrite's going to be one of these things that if no one does it by March, I'll start taking it seriously.  
Because, I mean, it'll just speed the whole thing up.  
It's how we're going to get Python speed.  
I don't know.  
My dream is, like, I want to turn the renderer and the compiler into graph rewrites also.  
And then graph rewrite 2.0 can support things like multi-core graph rewrite.  

##### **Chenyu** [[00:47:11](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2831)]  
Mm-hmm.  
Yeah, because every rewrite is kind of local.  
It's local, so you could definitely parallelize a lot of those.  

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2844)]  
Oh, yeah.  
You could totally, for all the functions, you could parallelize them.  
And you can also do speculative rewriting.  

##### **Chenyu** [[00:47:38](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2858)]  
You can.  
I'm not sure.  
How does that work?  
Don't you have a sequential nature?  

##### **Geohot** [[00:47:45](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2865)]  
Yeah, it's not that sequential.  
So there's a bunch of ways you can parallelize, right?  
Now we're just kind of making a big queue for them.  
But you can parallelize for free just where you do the matches.  
Like call all five match things at once.  
This is the beauty of UOPs being immutable.  
Okay, fine.  
It turns out that only two of them return when the first one was needed, right?  
So it's speculative.  

##### **Chenyu** [[00:48:12](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2892)]  
Okay.  
That sounds good.  
February already.  

##### **Geohot** [[00:48:20](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2900)]  
Well, my February is going to be all DSP and scheduling.  

##### **Chenyu** [[00:48:27](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=2907)]  
Yeah.  
Okay.  
I would comment on the sorting add chain stuff.  
So I discussed with I think the authors here.  
So I discussed the author on the PR.  
Basically, my main concern is  
If we're going to add more stuff into this, the order of ops or basically when we topolize a new op, how do we compare the order of lows?  
I want a better way to manage this because the worst case is we made a bunch of higher level tests and  
Maybe it's very difficult for this to pass if we ever want to refactor some part of the uop.  
And that's why I propose having a lower level, older test on stuff.  
But the author said he's thinking something else, and he's writing a report on that.  
So I'm waiting on that.  
Basically, I want to avoid the case that it might work now, but down the line, it would make future changes much more difficult, because you need like 10 pieces to click to pass a test.  
Otherwise, what's exciting about this stuff, I imagine it will also improve the kernel speed.  

##### **Geohot** [[00:50:04](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3004)]  
I've always imagined these tests looking kind of like UPats.  
They look like graph matchers that determine if the test passes instead of the strings.  

##### **Chenyu** [[00:50:22](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3022)]  
Yeah, maybe that's fine.  
isn't that copy your implementation to your test?  
What's stopping you from just copying the same UPat in the implementation?  

##### **Geohot** [[00:50:35](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3035)]  
Yeah, I don't know.  
Or maybe the other way to test this is to actually just evaluate these in Python on random values and see if the values are the same between the simplified and the unsimplified.  
Do like a test.  

##### **Chenyu** [[00:50:50](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3050)]  
Yeah, but then you are not really testing the behavior, which is some specified order of doing ALUs.  
I don't know.  

##### **Geohot** [[00:50:57](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3057)]  
Yeah, yeah.  
I don't know.  

##### **Chenyu** [[00:51:01](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3061)]  
Yeah.  
I think now it's probably fine.  
We just do one-off and think about a better way to do that.  
Yep.  
Not the biggest problem.  
Getting things done is more important than figuring out the perfect way to write tests.  
OK.  
Yeah, that's everything on the agenda.  
Do we have any questions, comments?  

##### **Geohot** [[00:51:36](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3096)]  
I have a few closing notes if anyone has questions.  
We have a little extra time today.  
I was just thinking as I was talking at dinner about  
How long it really takes before projects like this become really successful.  
You know, you can think about Linux started in the early 90s and it only really, it took like 10, 15 years.  
And then you think of how long Git took.  
Git was this early thing that was hosting the Linux kernel and now it's multi-billion dollar business.  
LLVM and Clang.  
I remember, I mean, I was there for Clang.  
I was there for, everyone used GCC when I was in high school.  
And then somehow in the 20 years that came after,  
everything switched to LLVM and Glang.  
That's how long it takes to really build these fundamental projects.  
But I see TinyGrad being a project that lasts 20 years.  
and being a major piece of infrastructure for all the software 2.0 stuff on both the operating system looking side and the compiler looking side.  
Because we're in this beautiful paradigm where compute is so much simpler to talk about.  
Even when you get to these complex things like mixture of experts, it's not really complex.  
Like the memory, the way that memory depends on values is so restrictive compared to programs, compared to like a web browser.  
So exciting times ahead and it'll be beautiful infrastructure for the future.  
But everything uses Clang, right?  
Like hip is Clang.  
Sure, some things in Linux might still use GCC.  
But hip is Clang.  

##### **Chenyu** [[00:53:44](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3224)]  
I think a lot of these softwares really has a selling point, even when they are not that mature.  
And it's very clear from the start what Clang is trying to do or what Git is trying to do.  
And they do these things pretty well.  
And they later broadcast into a much broader scope.  
I think TinyGrad's similar to that.  
Initially, it's for running inference on device for comma, then running inference on all kinds of hardware and make it fast, then move into training and distributed stuff.  

##### **Geohot** [[00:54:19](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3259)]  
We still have further to go with inference.  
If we get comma on the DSP, that'll be great.  
So it happened first half this year.  
I should say more LLVM than Clang.  
I mean, everything is LLVM-based.  
The Qualcomm shader compiler is LLVM-based.  
Metal is LLVM.  
It's Apple, but... Cool.  
Thanks, everyone.  

##### **Chenyu** [[00:54:55](https://www.youtube.com/watch?v=Wf9mQ0vVcHQ&t=3295)]  
Thank you.  
See you next week.  
Bye-bye.  
