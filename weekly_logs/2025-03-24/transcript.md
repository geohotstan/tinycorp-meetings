# 2025-03-24 Meeting

## Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time)
- company update
- quantized dsp
- bert
- scheduler
- driver
- tensor cores
- webgpu
- onnx
- retinanet
- torch frontend (test_ops, multi gpu training, torch compile)
- other bounties (AMD llvm backend)

## Audio

[Youtube Link](https://www.youtube.com/watch?v=eH_0eFcxDFA)

## Highlights

- [Company & GPU Update](#geohot-000004)  
TinyBox v2 cases shipped, 12x 5090s expected soon. Intel GPU deal abandoned due to product line issues, with focus shifting to AMD and NVIDIA.

- [Quantized DSP Progress](#geohot-000311)  
Hand-coded optimizations reach 118.5ms without BEAM; future plans include Z3-based constraint solving for ALU utilization.

- [Potential future using Z3](#geohot-000615)  
Constraint solving is how we get ahead of LLVM

- [BERT Training Optimizations](#chenyu-001123)  
Current step time at ~400ms (3h total). Key bottlenecks: embedding backward, dropout, and JIT memory spikes.

- [Memory Visualization](#qazalin-002049)  
New memory graph tool in VIZ identifies spikes (e.g., embedding buffers), aiding debugging for BERT and other models.

- [Driver & DSP Focus](#nimlgen-002845)  
Memory planner refactor for DSP (16-buffer limit); multicore DSP and RetinaNet hacks planned after Qualcomm contract work.

- [Tensor Core Priorities](#ignaciosica-003045)  
Focus on perfect-sized matmuls (e.g., BERT's 4 sizes) with async copies for 30% speedups, skipping padded cases for now.

- [WebGPU Refactor](#hooved-003516)  
Export logic simplified using core structures (e.g., ExecItem over custom classes), aligning with CUDA/Metal graph executors.

- [RetinaNet Stability](#flata-004535)  
AMD driver NaN losses under investigation; green box validation planned before TinyBox Red debugging.

- [Torch Frontend](#geohot-004951)  
test_ops PR near completion; multi-GPU training in progress; torch.compile blocked by C++ type issues.

- [AMD LLVM Backend](#geohot-005204)  
Merged with one test skip (rounding mode)

- [MI300X Future](#geohot-005445)  
Awaiting fast sync for 8-GPU scaling; BERT/MLPerf submission possible if performance is competitive.

- [New Bounty: Fast MoE](#chenyu-005612)  
$300 for 50%+ theoretical max speed on MoE via kernel fusion/rewrite rules.

## Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=0)]
Start with company updates?

##### **Geohot** [[00:00:04](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=4)]
We're supposedly finally going to get some 5090s this week.
So we'll see if that's true or not.
We got 12 5090s coming.
TinyBox v2 is shipped out, so we got cases coming for it.
Everything looks good.
We're just actually waiting on the GPUs, because I'm not paying those scalpers that much money.

##### **Geohot** [[00:00:32](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=32)]
The Intel deal is gone.
I wrote a thing about Intel.
It's... You know, AMD had to fix software.
Intel needs to do a complete 180.
I feel like it was worth writing up since I spent a lot of time diving into this stuff.
Both product lines are pretty much nonsense and dead.
Maybe Intel becomes interesting in five years when, if they manage to not cancel the A770 and B850 lines and keep going for five years and eventually build a big GPU and eventually work their way up to big accelerators, that's interesting.
But what they currently have now, not it.

##### **Chenyu** [[00:01:30](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=90)]
Are we still interested in there's one bounty that's something to do with A770?

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=99)]
Which one?
I could probably delete it.
There's no future in those cards.

##### **Chenyu** [[00:01:45](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=105)]
OpenCL.
This is probably fine.
OpenCL compile with opening device.

##### **Geohot** [[00:01:51](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=111)]
Honestly, I don't even think I'd merge it.
If someone actually did a good job on it, I'd pay the bounty out.
But I'm not maintaining an Intel link to some Intel thing that's going to be deprecated in two weeks, two months, two years, whatever.
It's not.
We shouldn't have even done the Intel TensorCores.
It got us nothing.
Maybe we'll take them out.

##### **Chenyu** [[00:02:16](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=136)]
Yeah, that's fine.

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=139)]
Yeah, Intel can use normal OpenCL.
I don't know.
They have weird Intel-only stuff.
There is no future in any of these platforms.
Yeah, I'll delete the matmul bounty for A770.
I think that's the only one.

##### **Chenyu** [[00:02:46](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=166)]
OK, sounds good.
That's company update.
OK.
Quantize DSP?

##### **Geohot** [[00:03:11](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=191)]
Good progress on that.
You can see that we're now at 118.5 milliseconds, and that's without BEAM.
So that's with no search.
That's just with some hand-coded guesses.
Similar to the GPU, BEAM is not that useful.
There's pretty clear ways to use the memory.
The coolest thing about the DSP project has been it makes it very clear.
If you gave me an FPGA and told me to build a GPU, I have no idea how to build a GPU.
But if you told me to build the DSP, I could build the DSP.
It's a very simple machine.
And the advantage of it being a simple machine is it's super low power.
I think that...
It's so sad about Qualcomm's sales and patent division because Qualcomm's chip division is actually amazing.
We were talking at lunch about how Qualcomm's chips are the only thing that's close to Apple in laptops.
No, and the DSP, I mean, it's good.
It's well documented.
There's a very clear way you have to use it.
It's not very flexible.
It doesn't support any kind of memory coalescing.
You have to, it doesn't have a good prefetcher.
It doesn't have anything like, it's an in-order core.
It has no lookahead.
Instead, it has VLIW.
Yeah.
I think if NimbleGen gets this part done, I think we should be good.

##### **Chenyu** [[00:03:45](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=225)]
Is BEAM not working?

##### **Geohot** [[00:03:48](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=228)]
It works.
It's just not faster.

##### **Chenyu** [[00:04:53](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=293)]
Interesting.
Are you adding rules to make it fast?

##### **Geohot** [[00:05:01](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=301)]
I could, but there are some more fundamental things to figure out first.
So it's interesting.
You can look at each kernel, and this is not like a GPU at all.
BEAM almost doesn't make sense, and you almost do have to hand code, and eventually we'll go to something.
I just went out for dinner, and I'm walking back, and I'm thinking, we've got to move to a Z3-style architecture.
Instead of rules, this is how we really bypass.
This is how we beat LLVM.
Like LLVM and TinyGrad now look very similar with sets of rewrite rules that can maybe merge the instruction, maybe can't.
But imagine instead you put all the instructions in a global constraint solver, and then you tell the global constraint solver, okay, how do I maximize my ALU utilization?
Like how do I keep everything on the ship fed?
Because that's the real thing you're trying to do.
So if I spent the whole rest of the year working on the DSP,
and managed to write a Z3 frontend to find amazing things for the DSP, it's so worth it.
It's the future.

##### **Chenyu** [[00:06:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=367)]
So you can use Z3 so presumably because you know your loss function pretty well.

##### **Geohot** [[00:06:15](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=375)]
Yes, you know your loss function, which is literally just saturation.
If I'm computing a certain number of flops, okay, cool, what's my ALU saturation?
That determines everything.
And not only do I have to maximize ALU saturation, I also have to do that subject to maximizing load saturation.
OK, if this is my bandwidth, this is my latency, what can I do about that?
I can think about something like a bank conflict.
You're never going to solve bank conflicts with rewrite rules, but you can totally solve bank conflicts with Z3.
So I think that that's the future.

##### **Geohot** [[00:06:58](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=418)]
Like, the more we can put these things into constraint solvers, and the more we can put the whole thing into constraint solvers, the more we can put all the scheduler stuff into constraint solvers.
Say, okay, minimize memory usage, minimize flops, minimize flops subject to this cost.
All that stuff is just possible to express.
These things are never going to be good in any other way.
So yeah, I will solve for this DSP.
But it's a hand-coded rule for 3 by 3 conv, basically.
If you want a 5 by 5 conv, well, you can either hand-code it, or you can put it in Z3.

##### **Geohot** [[00:07:43](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=463)]
It's never going to find it with BEAM or with stuff like that.
Search space is too big.
A lot of these things are even beyond BEAM.
do I want to do this rewrite or not?
For example, there is a function that does a multiply and then four-wide reduce.
Could you still use that function if it's only a three-wide reduce?

##### **Chenyu** [[00:08:18](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=498)]
I don't know.
Try, see if it's faster.

##### **Geohot** [[00:08:22](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=502)]
Or try, see if it's faster, yeah.
But the try, see if it's faster, that's not something that's in our current
BEAM search space.
That's something that would be applying a rewrite rule or not applying a rewrite rule.

##### **Chenyu** [[00:08:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=514)]
Yeah.
OK.
Anyway, I think we will see how this works.
Then we'll figure out what other common tricks that we will.
It's similar to a lot of flags that we currently just set on and off and applying BEAM on top of that.
I think those are similar.

##### **Geohot** [[00:08:56](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=536)]
Yeah, I see a whole....

##### **Chenyu** [[00:08:59](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=539)]
Yeah, any kind of either split kernel or not, fused Arange or not, partially fused Arange or not, or any fusion thing like that, I think are similar.

##### **Geohot** [[00:09:11](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=551)]
Yeah, I agree.
And then I think where this is how we get ahead of LLVM.
If we were to write something that goes straight to assembly using UOP rewrite rules, we're the same as LLVM.
But LLVM wishes they could do constraint solving.

##### **Chenyu** [[00:09:31](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=571)]
Yeah, don't they have Z3 as their dependency as well?

##### **Geohot** [[00:09:35](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=575)]
Only for testing, actually.
The Z3 is only for compilation.
It's not used at runtime.
I see.
They can verify the accuracy of their rewrite.
Basically, they can use Z3 to verify that their rewrite rules didn't generate anything fake.
But it's just for testing.

##### **Chenyu** [[00:09:53](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=593)]
OK.

##### **Geohot** [[00:09:55](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=595)]
So, yeah, I think, I don't know.
I think they'll be a little bit flexible on when we finish this contract, too, but we're getting there.

##### **Chenyu** [[00:10:05](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=605)]
Our contract look good?

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=607)]
Yeah, yeah, yeah.
They want me to push for the speed on the 845, even if it involves some hacks.
But, yeah, checked in with the guy.
We're good.

##### **Chenyu** [[00:10:16](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=616)]
Sounds good, sounds good.
OK, moving on to BERT.
Open to BERT.
Oh, so 85 is too hot?
Is there anything we can do to make it cooler?

##### **Geohot** [[00:10:32](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=632)]
Yeah, you can jack the fans up.
If you use IPMI tool, you can set the fans to maximum.
I think we have a thing for that somewhere.

##### **Chenyu** [[00:10:39](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=639)]
Because now I see 92, so it's clearly too hot.

##### **Geohot** [[00:10:47](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=647)]
Oh yeah, that's way too hot.
Oh, it almost seems like a fan broke.

##### **SPEAKER_02** [[00:10:52](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=652)]
I don't know.
I'm getting fans spinning.

##### **Geohot** [[00:11:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=660)]
Well, on the GPU, the fan's spinning.
So NVIDIA GPUs throttle at 82.
Any time you see stuff above 82, it's too hot.

##### **Chenyu** [[00:11:09](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=669)]
That's probably why, because I noticed starting from last night, like 12 hours ago, it got a few percent slower.

##### **Geohot** [[00:11:18](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=678)]
Yeah, let me see if I have the command to jack the fans up.

##### **Chenyu** [[00:11:23](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=683)]
OK, yeah, let's pick up separately.
I find several issue.
So I think there is an issue in JIT that when we do the replace buffer somewhere, there is a very likely
Double allocate buffer.
There's a small memory spike.
So for BERT, because it's so close to the limit, sometimes it will fail at last steps, depends on how many kernels you BEAM.
We have a threshold that adjusts how many kernels we BEAM.
And we don't BEAM if it's too big, for example.
And I was trying to increase that limit.
Then we start to see out of memory.
But if you BEAM those kernels,
separately first, then do a full run, then you never hit the memory limit.
So there seem to be some issue with JIT.
I work around this by turning off JIT, but still do BEAM and it work fine.
So I just like to fix that.
So that's legit memory spike issue land.
Also for NemoGen, if you are interested, AMD driver running the run is like 5% to 10% faster.
So for the script, I've currently BEAM set up using AMD driver and do the real run with AMD driver because that's faster.

##### **Nimlgen** [[00:13:02](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=782)]
Yeah, we'll take a look.

##### **Chenyu** [[00:13:05](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=785)]
Yeah, you can see my change in my script.
The last thing is our dropout.
So previously, I did some ablation to figure out the bottleneck of softmax, their known matmul, and
and dropout.
That's basically everything you have in your attention kernel.
And that's pretty much everything you have in the BERT training.
So for now, dropout itself is 10% of the step.
And that seems pretty slow.

##### **Geohot** [[00:13:44](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=824)]
Yeah, it's really slow.
Are we reading from an Arange?
Are we fusing that Arange or not?

##### **Chenyu** [[00:13:52](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=832)]
We are reusing that A range.

##### **Geohot** [[00:13:55](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=835)]
No, but not reusing.
No, it's got to be fused.
If it's reused, you're reading from it.
Reading from the Arange is slow.

##### **Chenyu** [[00:14:04](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=844)]
Reading from Arange is slow.
Yeah, it's slow, but it's also not that slow.
Why is reading from Arange that slow?

##### **Geohot** [[00:14:15](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=855)]
Because you've got to read from the whole thing.
How big is your piece of randomness?
Dropout has a huge random thing.

##### **Chenyu** [[00:14:23](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=863)]
Yeah, it's the same size as your embedding.
I don't know if we generate.
Well, that's another thing.
So for embedding, we are also generating dropout for the whole embedding weight.
Well, we really need the ones that's after we select.

##### **Geohot** [[00:14:41](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=881)]
Yeah, but there's some huge Aranges in that dropout.
Why can't we just fuse the Arange?
We have to just get it to fuse.

##### **Chenyu** [[00:14:48](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=888)]
Yeah, that's another issue.
The kernel in dropout is not fusing.
It has a cat.
It has weird stuff.
I was trying to rewrite that.
So it's basically doing two sets of rotation with uint32.
And there's a clever trick that stack each other.
So it's a uint64 and do some rotation thing on it.
I don't know.
I feel it might be faster if we just split the two and having two sets of things do their rotation instead of
Combining one into uint64, and we have other rewrite rules that break it up to 2 uint32 again, then do the math in uint32, then put it back.
These kernels you cannot fuse because it's a bit shift thing.
But if we split that into just two sets of uint32 altogether, it's possible.
That's why currently, even if you fix the integer div thing, it's still not fusing.

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=955)]
Yeah.
If we can just change the kernel to be fast, let's just change the kernel to be fast.

##### **Chenyu** [[00:16:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=960)]
Yeah, I plan to clean that up.
Anyway, this is like 10%, 5% to 10%, I think.
If we fuse ARange for just embedding, it saves like 2%.
It's like 7, 8 milliseconds.
So that we can add or we can hack just that part any time.
So it's just for reference.
uh and finally the backward for embedding it's interesting i post the script i use in scheduler channel uh similar to forward since you only select embedding for some like your batch to the same size as your sequence lens and your batch size you can
theoretically, your backward gradient update also doesn't need to be proportional to your variable size.
But I don't currently quite see how we fuse that or how do we rewrite that.
But that is also slow.
That's the reason why everything in our BERT step except the
transformer attention layers, the rest runs at 70 TFLOPs combined for around 66 milliseconds.
Very slow.

##### **Geohot** [[00:17:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1054)]
Across all 6 GBUs?

##### **Chenyu** [[00:17:37](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1057)]
Yes.

##### **Geohot** [[00:17:38](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1058)]
In BF16?

##### **Chenyu** [[00:17:42](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1062)]
In float16.
But the rest doesn't really have tensor cores.
It's just embedding and embedding backward.
And the loss is negligible, like one millisecond.

##### **Geohot** [[00:18:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1080)]
So it's just like softmax kind of stuff, like the maxes and stuff for data accessing memory?

##### **Chenyu** [[00:18:06](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1086)]
No.
So softmax is included in the attention layers.
So we have 24 attention layers.
Those are...
So out of 400 milliseconds, those 24 attention layers have like 350-ish millisecond, 340.
And the rest 60 millisecond is the loading the data, run embedding.
And your final loss hat, to loss hats,
and your backward and your gradient clip and stuff.
Loss and gradient clips are very cheap, like 2 milliseconds.
So it's mostly embedding.

##### **Geohot** [[00:18:53](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1133)]
I see.
Yeah, OK.
So we got to get Arange.

##### **Chenyu** [[00:19:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1140)]
Yeah, so embedding forward, if we just fuse Arange, that will work and saves you 7 milliseconds.
backward should also save some.

##### **Geohot** [[00:19:15](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1155)]
Cool

##### **Chenyu** [[00:19:19](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1159)]
And I think that's it.
So there's a path for us to be.
So now we are looking at 390, 400 milliseconds and three hours if it converges well.
So if we want to do two hours, then we need to find another 130 milliseconds.
I have a breakdown here in the channel.
I have another spreadsheet.
I check these things.
We'll see.

##### **Geohot** [[00:19:50](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1190)]
How bad is red?

##### **Chenyu** [[00:19:54](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1194)]
Red is like 70% of the speed.
It's roughly proportional to flops.
So I'm not too worried.
Other than like AM driver seems to be slightly slower.
other are pretty much proportional to flop difference.
So it really is, we improve these algorithms, and both will be fast.

##### **Geohot** [[00:20:21](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1221)]
Great.
I put the fans to full on Tiny14, by the way.
I don't see any jobs on there.

##### **Chenyu** [[00:20:25](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1225)]
Yeah, I just killed it because it was too hot.

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1229)]
You can start it again.
It should stay cool.

##### **chenyu** [[00:20:33](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1233)]
OK.
OK, I will try that later.

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1237)]
Cool.

##### **Chenyu** [[00:20:38](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1238)]
Yeah, so that's BERT, let's move on to scheduler.

##### **Qazalin** [[00:20:49](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1249)]
I did some work on the grouper, but then I moved on to, now we have a memory graph in VIZ.
So we can actually see the peaks in the usage.
Just with BERT, it's interesting.
I'm going to take a look at this one.
Yeah.

##### **Geohot** [[00:21:08](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1268)]
You got a picture to post?

##### **Qazalin** [[00:21:10](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1270)]
yeah sure just take a screenshot the first one you can also run some it's upstreamed on master i have some work i want to do on like referencing these stuff back to the actual kernel that runs so i think that would be an interesting addition to VIZ um yeah so we can actually like see these stuff now

##### **Geohot** [[00:21:38](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1298)]
Oh, interesting.
So you can really see that spike in there.
Oh, that's probably the embedding being stupid.
Oh, we're probably saving way too much for the embedding.
All right, that's what I'd imagine that huge purple thing is, like the embedding backwards.
Do you think that's right?

##### **Qazalin** [[00:22:13](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1333)]
So this is buffer 207.
I'm going to take a look.
I'm going to post a picture of all these.
But yeah, you really want to hover over this and see the full details of the currents with the codegens.

##### **Geohot** [[00:22:26](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1346)]
So wait, this is BERT at what batch size?

##### **Qazalin** [[00:22:30](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1350)]
This is at one schedule, one schedule step.

##### **Geohot** [[00:22:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1354)]
Well, it's one schedule step, but what's the batch size?
And this is a training thing.

##### **Qazalin** [[00:22:39](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1359)]
Yeah, this is batch size.
It's this picture.
So I'm running this one.
I'm running a tiny one on my Mac.

##### **Geohot** [[00:22:55](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1375)]
Interesting.

##### **Chenyu** [[00:22:58](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1378)]
So this is, I don't know, six?
Or 11, probably.
I think default is 11 times 2.

##### **Geohot** [[00:23:09](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1389)]
Those purple and blue ones look brutal.
It looks like, bigger than, that's the embedding.

##### **Qazalin** [[00:23:18](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1398)]
Yeah, it might be.

##### **Chenyu** [[00:23:20](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1400)]
Yeah, it's probably the embedding and the dropout.

##### **Geohot** [[00:23:23](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1403)]
Oh.
So what I see from that picture, I don't know if it scales to BERT Not Tiny.
Probably doesn't.
But we're wasting 2 thirds of the memory on the embedding.
I bet it's not the same with Not Tiny, but still.

##### **Chenyu** [[00:23:38](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1418)]
Yeah, because for embedding, if you do a dropout on embedding, you mask a lot of things out.
But you also don't need the random out of the thing you select.
But you still need it for your backward, something like that.
Cool.
Yeah, this is useful.

##### **Qazalin** [[00:24:10](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1450)]
So I'm working progress, making progress.
So yeah, I'm going to keep on improving this.

##### **Geohot** [[00:24:20](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1460)]
It looks great.
It looks like the PyTorch one, but better.
We can see the kernels, too.
PyTorch can't do that.

##### **Qazalin** [[00:24:31](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1471)]
It also works on all backends.
Torch is just CUDA.

##### **Geohot** [[00:24:35](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1475)]
Yeah, it's a CUDA tracer, of course.
Only CUDA knows the memory.

##### **Qazalin** [[00:24:40](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1480)]
And so VIZ=1, no extra stuff you need to do on your end.

##### **Geohot** [[00:24:45](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1485)]
Yeah, that's great.

##### **Chenyu** [[00:24:48](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1488)]
And does it show?
OK, so you eventually probably show which device the buffer is on and stuff like that.

##### **Qazalin** [[00:24:57](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1497)]
Oh, this is actually the purple one is the softmax.

##### **Chenyu** [[00:25:03](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1503)]
OK, interesting.

##### **Qazalin** [[00:25:05](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1505)]
It's the kernel.
Yeah.
This is the metadata of the kernel.

##### **Geohot** [[00:25:13](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1513)]
Yeah, I mean, we want to be able to click on it.
It should go to that buffer in your kernel.

##### **Qazalin** [[00:25:17](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1517)]
Exactly.
You want to jump to definition for functions in VS Code?

##### **Geohot** [[00:25:25](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1525)]
Nah, that stuff never works.
If you could just click the kernel and it shows what the metadata says, that's pretty good.

##### **Chenyu** [[00:25:39](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1539)]
I think for now, it's already useful.
If you do this, then you will start to see very bad or very big memory buffers.
That's a good debugging tool to start with.

##### **Geohot** [[00:25:52](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1552)]
Yeah.
And yeah, just like any way to find out what they are, then we can think about it.
Cool.
Great.

##### **Chenyu** [[00:25:58](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1558)]
Great.
Anything else?

##### **Qazalin** [[00:26:05](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1565)]
Grouper's a big project.
I'll try to make progress on it, but I see we need the Fuse Arange and stuff.
OK.
Yeah.
I'm going to see how to make progress on that one.

##### **Geohot** [[00:26:22](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1582)]
When I'm done with the DSP, I'll help you with the Grouper.
I'll help you think through what some of these things are.

##### **Chenyu** [[00:26:30](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1590)]
Yeah, I think two things I would help are this fuse Arange and the back-to-back type of multi-reduce.

##### **Geohot** [[00:26:43](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1603)]
You mean like the conv backwards thing?

##### **Chenyu** [[00:26:46](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1606)]
No, the norm.
You do a reduce and get the average or max, then you do element-wise on that kind of back-to-back reduce.

##### **Geohot** [[00:26:58](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1618)]
Oh, yeah, I know that.
Uh, I think that one's really hard.

##### **Chenyu** [[00:27:03](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1623)]
No, that was our dream two MLPerf ago.

##### **Geohot** [[00:27:05](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1625)]
Oh, I know.
I mean, like, ArgMax is doable.
ArgMax you can do.
If you're doing stuff where you're, like, subtracting the max of a list, that's super hard.

##### **Chenyu** [[00:27:16](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1636)]
Oh, because your store's...

##### **Geohot** [[00:27:22](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1642)]
Well, yeah, if you're trying to subtract the whole max of a list, you're going to need to somehow broadcast that max of the list across your GPU.
And there's not really going to do that.
I mean, maybe it's doable if the thing you're computing a max across is a small dimension, and that small dimension is all in locals.
But even then, that's hard.

##### **Chenyu** [[00:27:47](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1667)]
OK.

##### **Geohot** [[00:27:50](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1670)]
But fuse Arange, we should definitely be doing.

##### **Chenyu** [[00:27:56](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1676)]
I also posed some issue when I was going around with fuse A ange, some corner case that when we finally fix this, we'd like those to also be addressed and tested.

##### **Geohot** [[00:28:09](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1689)]
Oh, I also found a bug in the linearizer during the DSP stuff.
It's not a wrong bug.
It's just linearizer sometimes doesn't finish.
I have a fix for it.

##### **Chenyu** [[00:28:18](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1698)]
Is that the?
Same thing as the test linearizer failure 53?

##### **Geohot** [[00:28:24](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1704)]
It might be.
I have a fix for it in the DSP branch.

##### **Chenyu** [[00:28:30](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1710)]
OK.
You can claim the bounty if that fix that.

##### **Geohot** [[00:28:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1714)]
Sweet.

##### **Chenyu** [[00:28:37](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1717)]
Cool.
OK.
Let's move on to driver.

##### **Nimlgen** [[00:28:45](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1725)]
Yeah, so this week I'm going to spend working in DSP.
So the first step is the new memory planner.
We've been working on this today.
So to merge it, to master.
So the whole idea is that we want to make memory planner be able to plan everything into one big buffer.
So we need this for DSP, since it's limited to 16 buffers maximum.
So also should get better memory usage, like low memory footprint.
So yeah, I'm still testing this.
But I hope, yeah, tomorrow we'll know it.

##### **Chenyu** [[00:28:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1714)]
Is there a branch I can test?

##### **Nimlgen** [[00:28:38](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1718)]
Yeah, so there is a PR.
Yeah.
So yeah, after this memory planner, I'll focus on DSP graph and then multicore DSP.
So yeah, that's the plan for this week.

##### **Geohot** [[00:30:06](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1806)]
Cool.
Yeah, I'll give you, I guess once you get some DSP graph memory planner thing you're kind of happy with, I'll give you the command to run.
I mean, you can just copy it from my branch, just the command to run the retinanet.
And we're just going to need to hack, hack, hack to make this thing faster.

##### **Nimlgen** [[00:30:31](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1831)]
OK.

##### **Geohot** [[00:30:35](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1835)]
Cool.

##### **Chenyu** [[00:30:39](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1839)]
Let's move on to Tensor Cores.

##### **Ignaciosica** [[00:30:45](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1845)]
Hi.
Last week I have been mostly working on fixing Tensor Cores 3 emulation.
And most of the week I was working in a special requirement that we discussed today that it's not actually a requirement that was emulating the same Tensor Core
MemoryLayout as the local memory layout that's used for the emulation.
What we want to emulate is what each thread is responsible for loading from global and actually the elements that are computed from global memory.
So that's kind of done.
I'm going to post a summary of what we discussed in the PR I merged a few days ago.
And today, I was working in fixing tensor cores.
Again, this simulation for padded tensor cores.
But I'm not really sure that the problem is with the TensorCore simulation, but maybe the propagation of the mask.
I'm not sure how robust is the correctness of mask.

##### **Geohot** [[00:32:08](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1928)]
It's probably not correct at all.
Yeah, this is why I wouldn't focus on the pad.
I would focus instead on
just trying to get, like, what we need to do is we need to get speed on AMD and NVIDIA on normal, perfect-sized matrices.

##### **Ignaciosica** [[00:32:27](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1947)]
Yes.
OK.
Yeah, yeah.
Sorry.
Go ahead.

##### **Geohot** [[00:32:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1954)]
The L2 caches of these GPUs don't have enough memory bandwidth to keep up with a matmul.
So if you preload the specific stuff into shared memory using the async commands, and I believe both of them have async commands, we should be able to get matmuls that are like 30% faster.
And this will translate directly to BERT performance.
Are the kernels in BERT, are the matmuls in BERT padded?

##### **Chenyu** [[00:33:02](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1982)]
No.

##### **Geohot** [[00:33:03](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1983)]
Yeah, great.
Let's take whatever sizes those are, and let's make those ones super fast.

##### **Chenyu** [[00:33:10](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1990)]
Yeah, I can give you a list of size.
It's only like four different sizes.

##### **Geohot** [[00:33:17](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=1997)]
Perfect.
Let's just make those super fast.

##### **Ignaciosica** [[00:33:21](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2001)]
So you mean the main gains are after the correctness of the local buffering, it's going to be using the async you said?
Because what I tried,

##### **Geohot** [[00:33:39](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2019)]
Well, so first you have to get it correct with the local buffers.
And the local buffer shouldn't be slower.
But the way to really get speed is going to be to do the async copy.

##### **Ignaciosica** [[00:33:56](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2036)]
Well, that's the .. sorry.

##### **Geohot** [[00:34:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2040)]
Oh, and to more cleverly use the warp.
Like when we talked about there's two things to control.
We can control the layout of the local memory, and we can control which thread does the copies.
So by playing with which thread does the copies and making sure you're hitting memory coalescing in your globals, you can make things a lot faster.

##### **Ignaciosica** [[00:34:21](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2061)]
Yeah.
Well, thank you.
That's it for me.

##### **Geohot** [[00:34:25](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2065)]
Cool.
I think the way that we're going to evaluate this project is on 4090 and 7900 XTX,
how fast can we get the four matmuls in BERT to be?

##### **Geohot** [[00:34:36](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2076)]
Because that's super useful, and it will help us get better ML perf time.

##### **Ignaciosica** [[00:34:41](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2081)]
Great.

##### **Chenyu** [[00:34:43](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2083)]
Yeah, I'll give you a comment that runs BEAM and just do the forward pass and not backward pass.
Because forward pass really is mostly just matmul, and you can see how fast your improvements are for BERT

##### **Ignaciosica** [[00:35:05](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2105)]
Great, thank you.

##### **Chenyu** [[00:35:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2107)]
Okay, that's good.
Okay, let's move on to WebGPU.

##### **Hooved** [[00:35:16](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2116)]
Hey, so in the past week, I refactored the internal logic of the model export, trying to focus on, as we had discussed, being able to clearly see where's the data, where's the transforms, and the intersection between those, as well as having a clear distinction between those and the runtime ops.
And so I wrote a single data class or two data classes in the export code that capture all of the models
data and transforms.
And I think it's a pretty simple and easy to understand way.
It's basically just a bunch of buffers, as well as the kernels and the mapping between the buffers and the kernels, as well as the symbolic arcs.
And it's just, yeah.

##### **Geohot** [[00:36:18](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2178)]
So I see you have this data class called kernel call?

##### **Hooved** [[00:36:23](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2183)]
Yes.

##### **Geohot** [[00:36:24](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2184)]
How does that differ from exec item?

##### **Hooved** [[00:36:27](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2187)]
It's just a subset of information in the exact item.

##### **Geohot** [[00:36:30](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2190)]
Why not use the exact item?

##### **Hooved** [[00:36:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2194)]
Yeah, I could do that.
I'll try it and see if it's better.
I just thought this was more concise in terms of if you're actually rendering the stuff into different exported runtimes.
It's just more concise to use this abstraction than to pull it all out of the execitem.
Yeah, I can give it a try with the execitem instead and see if it feels simpler.

##### **Geohot** [[00:37:09](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2229)]
Cool.
And then export spec is equivalent to a JIT command queue.
So what I don't want to see really like ever in TinyGrad is the same structure repeated but slightly different.
So you're welcome to refactor these core structures.
And this is the stuff that really adds... The problem with writing stuff that doesn't use the core structures is stuff will change and then your stuff will break.
Whereas if you use the core structures and someone wants to update the core structure, the responsibility is on them to fix it.

##### **Hooved** [[00:37:52](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2272)]
Right.
OK, yeah, I'll give it a try to try to make it just as simple, but using the core structures and not defining these data classes.

##### **Geohot** [[00:38:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2287)]
Yeah, so kernel call is exec item, and export spec is captured JIT.

##### **Hooved** [[00:38:12](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2292)]
Right.
Yeah, I 100% understand what you're saying.
So yeah, I'll try it that way without defining the new classes.

##### **Geohot** [[00:38:24](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2304)]
Cool.
And you're welcome also to add helper functions to the main classes.
If they're generic and good helper functions, right?
I want to see TinyGrad look like one repo.
And when I look at this export thing, what I see is... I see why this is valuable from a sense of it's easy to merge.
It's one file.
And it's easy to merge into one file, sure, but it's hard to maintain.
Because now if someone updates an execitem, they've got to update both.
So yeah, I think you got it.

##### **Hooved** [[00:39:04](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2344)]
Yeah, I'll pass through everything and try to take all this into account.
I guess the other thing I wanted to mention is that the rendering
part is pretty verbose, like rendering everything into JavaScript, like all the runtime stuff.
It's a few lines to render the buffers and the kernels, but just throwing that out there, that rendering all the JavaScript that wraps around the Dawn runtime,
It's similar verbosity to our Python runtime that wraps around the non-runtime, just throwing that out there.
There's duplication, but in terms of just because it has to be a different runtime or different, it's JavaScript as opposed to Python.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2390)]
Yeah.
Yeah, I can't see that being.
I see.
It's kind of like, yeah, I think that's OK.
I'm less worried about that.
Yeah, and more like seeing, I don't think this should be an export.py.
I almost think that like export webGPU kind of belongs in the webGPU runtime because it's the same code.

##### **Hooved** [[00:40:22](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2422)]
Yeah, no, I thought about that trying to,
like merge it into ops webGPU, like the runtime stuff.
I guess the difference is that's executed at the level of the execitems at the kernel level, whereas this wraps, it sort of blocks all the kernels together and then fits those into the runtime.

##### **Geohot** [[00:40:51](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2451)]
Yeah, so what you're talking about is a graph.

##### **Hooved** [[00:40:55](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2455)]
Right, right.

##### **Geohot** [[00:40:57](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2457)]
That's where it should be.
I think, right?
If what you want to do, if the thing that you're looking like, and you could look at Clang Graph for how this works, if the thing that you're trying to write looks like, OK, I have this whole chunk of kernels, and I want to run them all kind of like one kernel, that's exactly what a Graph Executor does.

##### **Hooved** [[00:41:17](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2477)]
Yeah.
Yeah, exactly.
OK, so the Clang Graph, is that, if I just grep that, I'll find that?

##### **Geohot** [[00:41:25](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2485)]
Well, it was actually deleted.
But Nimlgen is adding it back to the DSP stuff.
You can look at the other graphs, too.
You can look at like CUDA graph, like CUDA graph or metal graph.
Metal graph is simple.
Metal graph is probably the best one to look at.

##### **Hooved** [[00:41:44](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2504)]
OK, so those are in the current tree.

##### **Geohot** [[00:41:47](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2507)]
Yeah, metal graph is in the tree.
Do you have a Mac?

##### **Hooved** [[00:41:51](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2511)]
No, I'm on Ubuntu.

##### **Geohot** [[00:41:54](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2514)]
You're on Ubuntu, uhh...
If you have CUDA, there's a CUDA graph too.

##### **Hooved** [[00:42:01](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2521)]
Yeah, I have an NVIDIA card.
I can use a driver.
Yeah, but I can do that.

##### **Geohot** [[00:42:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2527)]
OK.
So that's in tinygrad runtime graph CUDA.py.
And you can see kind of how it batches them all together.
And you can see what the, you know.

##### **Hooved** [[00:42:16](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2536)]
OK, I'll focus on trying to make it right in those respects.
And then we can revisit.
But after that's done, we're going to need to do a bunch of things.
like systematically looking at how the export is tested, you know, at the program spaces, the program space that goes into this and comes out of this, like maybe with fuzzers, you know, maybe adding more puppeteer tests or, you know, model validation tests, things like that.
But yeah, the focus, the highest priority is to do what we just discussed.

##### **Chenyu** [[00:43:03](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2583)]
That sounds good.
OK.
And also, Wpmed fixed my webGPU pass issue.
So thanks for that.
Any update for ONNX?

##### **Geohot** [[00:43:27](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2607)]
I see stuff in...
In general, I added TinyGrad frontend ONNX this morning.
It's just a stub like the PyTorch one.
But yeah.

##### **Chenyu** [[00:43:43](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2623)]
We also merged the main script to test Hugging Face ONNX model and its coverage.
I run it locally.
We can verify the top 100.
And now it's just taking very long on CI.
So I think the idea is to, for now, just pick a few and make it clear how to.
So there's the script that generates some config by connecting to the internet, see what's the top downloading model.
Then there's a separate script that take into the first script and download the model, run the model, validate the implementation and stuff.
I think for now, you can just
and pick some model, generate the intermediate config.
I don't know, pick five models that you believe has the best coverage, maybe cover most of the ONNX up or something, some metrics you'd like, then we can test that in CI to start with.
I think that's enough for that bounty.
The true float16.
OK, yeah.
So our ONNX use float32 instead of float16 now because of numerical issues.
I think this is similar to quantize.
As long as we find a way that's close enough, I think we are good.
But 10% seems a lot.
Next, we'll move on to RetinaNet.

##### **Flata** [[00:45:35](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2735)]
Hello.
So far, progress-wise, I thought the AM driver was actually stable, but I got that odd loss that I had, I think, a few weeks ago back again when I was training.
And also, too, what I found out was that
After I do, I guess, probably more than two benchmark runs, I would notice that it would start returning loss as NaN already using the AMD driver.
So yesterday, I was able to actually get some pretty stable training using the AMD driver
um for that so that that seems to work i think there's just one issue that i saw that the that those fronts failed but also i noticed that the regression loss was not going in the down in the same fashion as the classification loss so i'll investigate that as well so that's pretty much my focus for for this week and i guess in the meantime i'll also try to refactor more things out of the main pr um
like the model eval changes that I made into smaller PRs so that it can be simplified further.

##### **Chenyu** [[00:46:41](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2801)]
Yeah, so I'm interested in that more because I think before we go dive into TinyBox Red and its driver issue, we want something that runs and is correct.
presumably on tiny box green.
So let's get that in so we know all the differences that will be coming from the red, then we can dive into to see if it's driver issue or any other issue about AMD.

##### **Flata** [[00:47:16](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2836)]
OK, sounds good.
Yeah, I'll start moving on to the green boxes for the green box for now and start training in there.

##### **Chenyu** [[00:47:24](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2844)]
Yeah, that's just making sure the new changes, the eval are all in.
I think we merged a bunch of stuff.
I think it should be doable in one or two more PR.
Then I'm happy to verify.
The green is correct.
It's always good to have something that's correct and to compare with to see what's the performance.
For example, you say the regression loss should go down.
I don't know if that's the case unless I see a complete around that show that's the case.
Things like that helps.

##### **Flata** [[00:47:59](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2879)]
Right.
I was comparing it with what I got in float32.
But I'm trying with float16 now.
But I do want to have, I guess, a correctness run in float16 in this case.

##### **Chenyu** [[00:48:15](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2895)]
And also a small thing, you might want to tune your loss scalar.
My experience in both ResNet and BERT is too small or too big, you will get NaN fairly consistently.
There's a range that it will work.
And this range can be different on red machine and green machine for whatever reason, because their precision or the things are slightly different maybe.

##### **Flata** [[00:48:45](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2925)]
OK, because I got better loss curves, especially in the classification loss with a lower scalar, because I copied the one from ResNet, and then I just kind of went down from 256 to 64.
So I'll see how the green box will look on that one.

##### **Chenyu** [[00:49:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2940)]
Usually for BERT, and I don't know for ResNet if it's similar, it should go up, because otherwise your gradient might underflow.
But I mean, your model might be different.
If you can check other people's submission to see if they set that value, maybe that's another reference to start with.
OK, sounds good.
So none is very relevant to Loss Scalar.
And that's the main reason people stop training using float16 and use bfloat16 and other formats.
It's just very annoying.
But otherwise, progress sounds good if you have new PR for review.
OK, um, Torch frontend?

##### **Geohot** [[00:49:51](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=2991)]
So I've just been merging tocubed, who's not here, has been making great progress on it.
So I've pretty much been just merging what he puts, and it's getting slowly better.

##### **Chenyu** [[00:50:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3007)]
There's a PR for test ops.
It's almost ready.
we find some small issues that sometimes the shape and stuff would probably be wrong.
I don't know if it's fixed by this latest, like, last PR code.

##### **Geohot** [[00:50:25](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3025)]
It might be fixed by what I just merged, yeah.

##### **Chenyu** [[00:50:29](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3029)]
Yeah, OK.
Otherwise, I think that one is quite ready There are some small hacks and stuff or things that Tinygrad doesn't support or doesn't support well I think lowers are fine for the scope of Bounty So that one should be close, I think, this week multi-GPU is from ToCube and I don't know if it is here, but
That one seems to be making progress.

##### **Geohot** [[00:51:02](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3062)]
I think he's making progress.
I locked it to him, right?
Oh, yeah.
So good.

##### **Chenyu** [[00:51:08](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3068)]
Yeah.
Yep.
So I think so far, everything moving.

##### **Geohot** [[00:51:16](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3076)]
Compile, unfortunately, it's going to require some C++ hacking.
If you pass in types to the compile and they don't have a storage, it gets upset.
So I don't know.
If someone figures out how to do the bounty, then great.

##### **Chenyu** [[00:51:48](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3108)]
Let's finish the first two, and maybe the authors are interested in doing more after that.

##### **Geohot** [[00:51:57](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3117)]
That seems good.

##### **Chenyu** [[00:51:58](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3118)]
OK.
AMD LLVM backend.

##### **Geohot** [[00:52:04](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3124)]
I just merged it.
I think it's good.
I think, yeah, I think bounty's claimed.

##### **Chenyu** [[00:52:11](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3131)]
OK.

##### **Geohot** [[00:52:11](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3131)]
Yeah, no, I dragged on that one a bit, but I think it's clean now.
There's one test skip on test div rounding mode.
I don't know about that one.
I don't want to change the whole LLVM thing for that one thing that doesn't seem that important.
Change the LLVM fast math string.

##### **Chenyu** [[00:52:39](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3159)]
Is it incorrect, or is it just slower?

##### **Geohot** [[00:52:43](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3163)]
Currently, it's incorrect.

##### **Chenyu** [[00:52:49](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3169)]
We might want to fix it somehow, or at least a third or something.

##### **Geohot** [[00:52:56](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3176)]
Specifically, what's incorrect is the rounding mode.
How much do we care?
It should never affect training.
All right.

##### **Chenyu** [[00:53:13](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3193)]
I don't know.
Probably fine.
We certainly spend like...
hundreds of lines in Tinygrad repo just to figure out all the different rounding mode stuff.
It might not need to be like a LLVM compile flag fix, but fix more upstream.
But ideally that should be handled.

##### **Geohot** [[00:53:40](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3220)]
Oh, well, I mean, we can, so there's a way he had to fix it.
He removed the, basically he used
really slow division instead of the RCP function.

##### **Chenyu** [[00:53:50](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3230)]
Yeah, I don't think we don't want that in general, but maybe specifically for a scale case, you can rewrite it at higher levels.

##### **Geohot** [[00:54:00](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3240)]
So you don't forget that.
Yeah.
But it's also, it's not even enabled by default.
I think maybe we can move to it.
But yeah, I mean, we should be able to try all LLVM stuff with AMD LLVM equals one, and maybe we'll magically get speed up.

##### **Chenyu** [[00:54:19](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3259)]
OK, I will try that.
I don't think we will magically get speed up, but we will see.

##### **Geohot** [[00:54:24](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3264)]
Oh, it's the new LLVM.
Chris Lattner fixed something, or somebody fixed something.

##### **Chenyu** [[00:54:30](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3270)]
Yeah, always have hope.
Ok.
You want to briefly touch on MI300x?
We finished the agenda.

##### **Geohot** [[00:54:45](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3285)]
Yeah, no, I think UUVN's been making good progress on refactoring the stuff.
We'll get that merged in soon.
Hopefully these, I mean, we should decide.
We should definitely try to get BERT running on it, and if our time isn't too embarrassing, we'll submit to MLPerf.

##### **Chenyu** [[00:55:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3307)]
Yeah, just let me know when it's ready for a more serious run, and I will prepare a run for that.

##### **Geohot** [[00:55:13](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3313)]
Yeah, I mean, I think we should definitely get it merged to get AMD working.
Unfortunately, for like Llama now, it's slower than HIP, and there's a chance it's fundamental.
So we don't really know how... The MI300X has eight GPUs in it, basically, and they have to be synchronized, right?
So it distributes the work to eight GPUs.
They share memory, so it's easy to distribute the work, but...
They then need to be synchronized.
And right now, we're using the same way of synchronizing them that you'd synchronize across, like, GPUs that are separated by PCIe.
So it's going all the way to VRAM to synchronize.
It's possible that that's the only way exposed over PM4.
I really hope it's not.
But, yeah, I think UUVN, I will just get something working.
We'll get that merged, and I'll throw another bounty up if you can figure out a fast sync.

##### **Chenyu** [[00:56:12](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3372)]
Oh, speaking of adding bounty, I think we also want to follow up bounty on MoEJIT.
Make it fast.

##### **Geohot** [[00:56:21](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3381)]
Oh, yeah.

##### **Chenyu** [[00:56:23](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3383)]
I think that one might have a similar issue to embedding backward in the sense that I'm pretty sure for now it's only 0, like multiply 0 for the things you don't need.
But really what you want is don't compute what you don't need at all.

##### **Geohot** [[00:56:41](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3401)]
All right, so we'll say fast OLMoE in TinyGrad, 50% plus of theoretical max.
That should be doable.
We'll get like 90% of the llamas and stuff on M3 max, whatever I have.
Yeah.
So $300 on that.
I think we both cleaned that up a little last week, though.
Yeah.
New bounty, $300.
Fast OLMoE on Tinygrad.
So you'll basically need to actually get the, it might just be as simple as writing two rewrite rules.

##### **Geohot** [[00:57:34](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3454)]
It might be as complex as getting two kernels to fuse.

##### **Chenyu** [[00:57:47](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3467)]
OK, I think that's pretty much it.
We will see if your linearizer thing fix other stuff.

##### **Geohot** [[00:58:03](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3483)]
Yeah, I'll put that up as a PR tomorrow morning.

##### **Chenyu** [[00:58:07](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3487)]
Good.
OK.
I think it was a pretty good week.
Pretty productive.
Many to do's for this week.
See you next week in Hong Kong.

##### **Geohot** [[00:58:21](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3501)]
Sounds good.
Looking forward to it.

##### **Chenyu** [[00:58:25](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3505)]
Bye.

##### **Geohot** [[00:58:26](https://www.youtube.com/watch?v=eH_0eFcxDFA&t=3506)]
Bye.
