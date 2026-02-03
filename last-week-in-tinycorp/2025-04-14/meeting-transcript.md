# 2025-04-14 Meeting

### Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time)
- company update
- chip!, fast python
- bert, MLPerf
- scheduler
- driver
- WebGPU
- retinanet
- torch frontend multi gpu
- cloud scale uuuvn stuff (be concise!)
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=4p_uWDeaO_8)

### Highlights

- **[Company Update](#geohot-000010)**: Geohot discusses agreeing to overpay for 100 GPUs (5090s) due to fluctuating tariffs, impacting pricing; the price of TinyBox V2 may increase for new orders, though two pre-paid orders will retain the original price.
- **[Chip Development](#geohot-000234)**: Geohot explores the feasibility of developing a custom chip, suggesting a simple design without an L2 cache, potentially using shuttle runs for cost-effective tape-outs (e.g., $300K for 6nm).
- **[Fast Python](#geohot-000944)**: Geohot reports a PR that reduces Python execution time by 30% by compiling UPat to Python functions, with potential for further optimization.
- **[BERT and MLPerf](#chenyu-001312)**: Chenyu updates on BERT MLPerf runs, noting stability on MI300 and Tiny Green, but NaNs and slowness on the Red system with the AM driver; plans to improve fusion and memory handling.
- **[Scheduler](#geohot-002106)**: Geohot explains the addition of a "kernelize" step to group operations into kernels, separating it from the scheduling toposort, alongside multi-output kernel support.
- **[Driver Issues](#nimlgen-002211)**: Nimlgen addresses AM driver slowness (fixed ring reduce) and NaNs, plus progress on USB GPU functionality with a firmware tweak.
- **[WebGPU](#hooved-003242)**: Hooved works on smaller PRs to learn the codebase, including fixing Viz buffer GC and memory optimizations for WebGPU.
- **[Retinanet](#flata-003425)**: Flata notes the main PR is merged, focusing on TinyBox FP16 runs, addressing NaNs, convergence, and slow eval speed (120% of training time).
- **[LLVM](#b1tg-003831)**: B1TG identifies slowdowns in the AMD backend due to HIP loop unrolling, optimizing with split options for speed.
- **[Cloud Scale](#geohot-004249)**: Geohot mentions buffer changes and Cloud Graph improvements for scale-out support, recently merging the fast pattern matcher.
- **[Bounties](#geohot-004712)**: Geohot lists open bounties: $500 for flash attention, $500 for unsigned firmware on 7800 XTX, $300 for 5090 NV backend support, and others for Torch and Llama4 Scout.


### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=0)]
OK, sounds good.
Welcome everyone.
Let's start with company update.

##### **Geohot** [[00:00:10](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=10)]
So I agreed to overpay for 100 GPUs.
So we're going to get 100 overpriced GPUs.

##### **Chenyu** [[00:00:22](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=22)]
Oh, the 5090s?

##### **Geohot** [[00:00:24](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=24)]
Yup.
Oh, this is just.
And then the tariffs are gone and then the tariffs are back and then get fucked.
You're paying more.
That's the only, that's the only lesson I took away.

##### **Chenyu** [[00:00:43](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=43)]
Wouldn't it be nice if there was like a GPU future price that you can lock in?

##### **Geohot** [[00:00:49](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=49)]
Well, that's what I thought having a signed contract was, but nope.
Rugged!

##### **Chenyu** [[00:00:57](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=57)]
Okay.
Do you know when will we be getting those machines?
I mean, GPUs?

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=65)]
Nope.
Oh, no.
No, no, no.
You don't get to know that either.
You just get a higher price for some GPUs in the hypothetical future.

##### **Chenyu** [[00:01:14](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=74)]
And when do we need to pay?
Like wire?

##### **Geohot** [[00:01:18](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=78)]
Yeah, well, at least we don't have to send the wire until they're ready to ship.
They just want to lock us in at the higher price.
Yep.

##### **Chenyu** [[00:01:29](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=89)]
OK, let's hope that's for only this hundred.
And now the next, I don't know, few hundred?

##### **Geohot** [[00:01:38](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=98)]
Your guess is as good as mine.
If this stuff actually stays, everything's going to get way more expensive.

##### **Chenyu** [[00:01:44](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=104)]
Yeah.
OK.
We'll see how that goes.
So what do we do with the V2 orders?
Do we increase the price?

##### **Geohot** [[00:02:02](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=122)]
We'll probably end up increasing the price of the box, but I don't know.
We only have two.
I'm going to honor those two.
I'm going to honor those two with the original price, the two that actually paid.
There's two that paid in full, and I'm not going to raise the price on them.
But to new people, yeah, the price will be higher probably.

##### **Chenyu** [[00:02:27](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=147)]
Okay.
That sounds fine.
Okay.
Let's move on.
You want to talk anything about the chip?

##### **Geohot** [[00:02:34](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=154)]
Uh, well, yeah, I mean, that's kind of the, I don't know, the more I think about it, the more I think we actually are going to do a chip.
It's like, it's not that crazy.
I see all the steps that it's going to take to get there.
We're not going to do it soon, but I think we'll get to a point where it's almost just so easy to do a chip.
We still have to solve the, like, I had a good conversation this morning on custom hardware with Fleetwood.
Maybe we don't need an L2 cache.
Like, GPUs all have this L2 cache.
If we don't need an L2 cache, if we don't need an L2 cache, Tenstorrent looks a lot more attractive.
Maybe Tenstorrent just kind of does have it figured out.
I mean, I still want to..
get to the point where where we can have our own chip but this this is going to be very like simple when it's time if if we could build something that just has to tile we build one simple core uh and there's no there's no l2 cache there's like global memory we can even hang it off an edge like tenstorrent um if we can do all that stuff then yeah making a chip becomes a lot simpler because the key to making chips it turns out
is that you want to do these shuttle runs.
So if you have a chip that's just the same design tiled over and over again, you can actually get that small design taped out quite cheaply in a shuttle run where you share the shuttle with everybody else.
And this is on the order of like, it's like 300K for six nanometer even.
And that prevents another big cost of these things, which is IP blocks.
If you want DRAMs and networks, you need to pay to license analog IP.
And this is millions of dollars.
But if you're taping out what's basically pure digital and all you want is like SRAMs and some LBDS to talk to an FPGA, that's all included in the library with the
that the chip manufacturer gives you.
Yeah, I see all the steps to get there.
It's all a software problem.
TinyGrab needs to be basically outputting fast assembly for GPUs and DSPs.
And then once we're there, maybe we'll even need a tenstorrent backend before we do our own chip.
It should just be so easy to build these backends once we have the right libraries that
Yeah, that's kind of all.
Then we're ready to make a chip.

##### **Chenyu** [[00:05:20](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=320)]
So as assembly backend, then maybe something like a Tenstorrent backend?

##### **Geohot** [[00:05:31](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=331)]
Yeah, there has to be no reason we can't support Tenstorrent.
Tenstorrent is, if you thought DSPs were hard, get ready for Tenstorrent, which is even harder.

##### **Geohot** [[00:05:46](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=346)]
Like, at least?
We got what?

##### **Chenyu** [[00:05:52](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=352)]
We got DSP pretty much figured out.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=356)]
Oh, yeah.
We got DSP pretty much.
Well, not exactly.
You can look in that branch.
There's a lot of hand-coded crap for that one model.

##### **Chenyu** [[00:06:04](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=364)]
Yeah.
I mean, of course, there are DSP-specific instructions that we are not fully using those.
And maybe there's some upcasting stuff that needs to be done.
But it seems straightforward.
I don't know.

##### **Geohot** [[00:06:25](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=385)]
Well, those are not even that.
The instructions themselves are pretty simple.
It turns out that data flow, it's not like the instructions are just basically different ways of triggering ALUs, whatever.
It's not that important.
But what matters is your data flow.
What matters is think of how your data is flowing through your whole network and then think of what your.. So the Qualcomm DSP has this 128-wide..
vector register, and then the main instruction that gets you flops, the DSP tensor core, so to say, it's not really a tensor core, is this multiply two vectors together and then do four wide reduces, like take each chunk of four and then reduce that into N32.
And that's like the main instruction.
So now optimize everything to use that instruction, basically.
But the DSP forced us to only soft consider memory.
So there's an L2 fetch and an L1 fetch instruction, which will prefetch things.
And you have to use them in order to get speed.
But you don't have to use them for correctness.
I think we'll get to a point where
I mean, you've got to make sure that you're doing those fetches perfectly.
Things aren't falling out of the cache.
This is where software needs to get to kind of before.
So yeah, like getting perfect speed out of the DSP is kind of a prerequisite for like our own chip.

##### **Chenyu** [[00:07:53](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=473)]
I kind of don't have a good cost model for like these memory fetch thing.
I think you just check their generated code and hand tune those.

##### **Geohot** [[00:08:07](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=487)]
It's not even that.
It's basically just if you're going to access something, you want to do an L2 fetch command 100 cycles before you access it.
And you want to make sure that the size of your L2 fetch is under 8 kilobytes or something.

##### **Chenyu** [[00:08:25](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=505)]
I think we will have a similar problem in multi-GPU or even multi-machine.
there are usually places that you can decide your copy order and your compute order.

##### **Geohot** [[00:08:40](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=520)]
Yeah, it's all the same problem, just repeated over and over again at different layers of the stack.
So yeah.
And then until like, I mean, in some ways, Tenstorrent maybe just as the right design.
Like, like, Tenstorrent is the ultimate hard one to code for.
But fundamentally, look, like, Google's like, the TPU is almost easier to code for than Tenstorrent.
But the TPU scale out is a mesh, is a torus, the same way Tenstorrent is a torus.
So you're not getting any benefit to just, like, even if you don't have to use the rings on the one thing,
If your fundamental connectivity is going to be a ring, which I think it has to be, then why not solve the ring problem at small scale too?
So yeah, Tenstorrent has it right.

##### **Chenyu** [[00:09:29](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=569)]
Cool.
Great.
OK.
Anything you want to say for Fast Python?

##### **Geohot** [[00:09:44](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=584)]
You can read it's FP underscore match.
I'm almost ready to merge it.
I don't know why this autogen test is flaky.
I don't know why some of these tests are flaky.
But why is this test flaky?
Setup environment keeps failing?
I don't get that.
And yeah, I have to make sure this benchmark test passes.
But it's about 30% speed across the board Python time.
So it should reduce Python time 30% on everything.
And you can try it.

##### **Chenyu** [[00:10:17](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=617)]
Is that the case for LLaMA, like unjitted LLaMA?

##### **Geohot** [[00:10:28](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=628)]
It should be, yeah.
It should be.
So about half the time was spent in match, and match is now like 4x faster.

##### **Chenyu** [[00:10:39](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=639)]
Great.
You can claim the function once you merge it.
Yes.

##### **Geohot** [[00:10:43](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=643)]
You have the first two.
Yeah, I can claim the first two.
And the last one's doable, too.
So I've still kept it to basically what I'm doing is just compiling the UPat to a Python function.
And I can go further, I can go way further with this.
Like there's so far you can go down this rabbit hole of realizing that the UPats, like currently I'm just looping to the UPats and matching them.
You don't have to do that.
You can design some, it's a decision tree basically.
You can factor some decision tree, you can figure out what your branching factor can be, you can start doing dictionary lookups, or I don't know if the match case statement in Python is fast.
Hopefully it is.
Hopefully that's basically O(1) and not O(n). But yeah, you just got to start doing micro benchmarks.
Diminishing returns at this point, though.
Most of the slowness is just in.. 

##### **Chenyu** [[00:11:32](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=692)]
I know you used a Python match.

##### **Geohot** [[00:11:37](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=697)]
I used.. I compile Python.
I just generate Python.

##### **Chenyu** [[00:11:42](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=702)]
Yeah, I think Python match is fast.

##### **Geohot** [[00:11:46](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=706)]
What do you mean, Python match?

##### **Chenyu** [[00:11:49](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=709)]
I thought you used Python's match statement?

##### **Geohot** [[00:11:52](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=712)]
Oh, I don't use Python match.
But you can use Python match.

##### **Chenyu** [[00:11:55](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=715)]
Oh, OK.

##### **Geohot** [[00:11:57](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=717)]
I don't know yet.
Is match case better than a whole bunch of nested statements?
Hopefully it is.
But you've got to start doing micro benchmarks to get this stuff.
But 8x was definitely possible.
That was a totally claimable bounty for anyone.
I don't know why nobody did.
It wasn't that hard.
It took me a week to get $2,000.
And it didn't really require specialized knowledge.
So I'm surprised no one claimed that bounty.
It just wasn't that hard.
And then you can push forward into compiling these things all together.
I can also start.
So right now, I'm still doing a function call to the function that the pattern match are like.
But say you have something dumb, like x plus 0 is lambda x:x.
You should be able to look inside the lambda x:x and be like, oh, wait a second.
I can just return x if I ever see this pattern.
So that's another optimization here that'll get you a couple more percent.
But I think the main thing I'm going to look at for the rest of the week is the linearizer.
Why is the linearizer so slow?
I can make that twice as fast.
There's another 10% to overall speed, 20%.
Yeah, so good progress on that.

##### **Chenyu** [[00:13:12](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=792)]
Looks like it.
OK, next we have our BERT and MLPerf.
I post the current status for our three system during the weekend I run.
So for BERT MLPerf, we need 10 back-to-back runs.
Previously, we used two or three machines and run for two or three days.
Now it's slightly faster, so I generate the runs.
MI 300 ones, everything looks fine.
It's pretty stable.
I imagined maybe with the Python speed or some small tuning, it can be less than 100 minutes.
Tiny green, similar story.
also relatively stable.
That's nice.
And so all our conversions is, I don't know, like 20% higher than the reference.
But the reference is also, I don't know, it's reference.
I don't see other people hitting that number.
But they are also using larger batch size.
So I don't know.
The red is the one that I was struggling with.
So for one thing, if a red machine ends, it doesn't crash the process.
So I really need to check if it's hanging.
That's one thing.
I added a check to crash if the loss becomes NaN.
Then I report I got a bunch of NaNs from amdriver that
I'm not sure if it's AM only, but previously I was running using AM for BEAM Search and Setup and using AMD to run, and that seems fine.
But again, each full run took six hours, and I don't even know if it's like some machine is bad or something.
I think for me, I'd like to.
So I use the MLPerf logging checkers to make sure for the MI300x and the green that I have 10 runs.
All the runs are logged correctly.
The numbers are fine.
So these two, I have more confidence now.
The red, since it's the, I really want to submit with our own driver.
And I'm happy to help testing it or
like spam running these.
But it's really not stable, and it's still like 5% slower than AMD.
So for me, I'm making sure these look stable and fine.
I want to add some of the Fusion tricks that I'm adding.
There are some weird problems in my runs that I will try to find a smaller repro and see how we can fix those.
That's Bert.

##### **Geohot** [[00:16:16](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=976)]
Cool.
Oh, good.
Yeah, I don't know.
Why is the AMD one NaN-ing?
Are you using FP32 output tensor cores?

##### **Chenyu** [[00:16:31](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=991)]
No, it's FP16.
But again, the same code runs with script.

##### **Geohot** [[00:16:40](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1000)]
No, I understand, but NVIDIA's tensor cores are more numerically stable than AMD's.

##### **Chenyu** [[00:16:49](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1009)]
Oh.
Is there document on these?

##### **Geohot** [[00:16:51](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1011)]
No, but it's just because of how they work.
I mean, it's like, so the RDNA3 tensor cores aren't real.
They're just using the ALUs.
So there's no actual instruction on RDNA3 which does this cross-reduce.
So it's just feeding it back into the ALUs.
Whereas the NVIDIA Tensor Core is doing an actual reduce on the width of the Tensor Core.
And it can add them up all at once for the maximum numeric stability.

##### **Chenyu** [[00:17:19](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1039)]
I see.

##### **Geohot** [[00:17:21](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1041)]
This is fixed in RDNA4.
But yeah, no, the RDNA3 Tensor Cores aren't real.
So I would really use them with FP32 output if that's easy to change.

##### **Chenyu** [[00:17:30](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1050)]
OK, if we want to do that.
I was also looking into how to fix the don't realize expand thing.
That certainly saves memory, but it doubles the speed on some other kernels.
I can look into this.

##### **Geohot** [[00:17:45](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1065)]
Well, I mean, we already have to for the MI300.
We already have to do fp32 accumulate.
There's no fp16 accumulate.

##### **Chenyu** [[00:17:53](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1073)]
But for the smaller TinyBox, we are bound by memory.
So it's a lot slower to drop.

##### **Geohot** [[00:18:01](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1081)]
How about this?
You can just hack the tensor core if you want to just use the FP16 to accumulate all that.
It shouldn't change the memory at all.
If something's changing the memory, something else is broken.
But you can't really use the FP16 to accumulate some red.

##### **Chenyu** [[00:18:22](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1102)]
OK.
That might be the reason.
Oh, I don't know.
I can try that.
And maybe later, when we talk about retinanet, we can also discuss.
Because retina net also has some NaN issue, but I'm pretty sure it's using float32 for accumulate.
So there might be fundamental issues in the rest stack, but I would try the tensor core swap thing alone.

##### **Geohot** [[00:18:53](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1133)]
Interesting.
Yeah, I mean, there might be other issues.
But I do know that the tensor cores, I mean, they just have to be less numerically stable because of how they work.

##### **Chenyu** [[00:19:02](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1142)]
Yeah, yeah, yeah.
OK.
That only makes sense.

##### **Geohot** [[00:19:05](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1145)]
I don't know if that's it.
I mean, it could totally be that we're so far within a realm of, yeah.
Yeah.

##### **Chenyu** [[00:19:11](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1151)]
OK.
No, that's good enough.

##### **Nimlgen** [[00:19:17](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1157)]
By the way, are we running with the same seed?

##### **Chenyu** [[00:19:21](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1161)]
What's that?

##### **Nimlgen** [[00:19:22](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1162)]
do we run them with the same seed?
Is it reproducible?

##### **Chenyu** [[00:19:29](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1169)]
Not really.
Not really.
I mean, I'll think about if there's a way to make it reproducible.
For now, the thing I'm seeing is it started wrong, and all the metrics look fine.
But an hour, two hours in, you suddenly get an app of less than that.
So I think previously, people hacked around this by saying, you can..
This is how people previously do mixed precision training, that you can kind of undo your update if you have a or something like that.
But at this point, I don't really want to change our model code.

##### **Geohot** [[00:20:13](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1213)]
I'd much rather just fix whatever is changing to be ready to accumulate.
Yeah.

##### **Chenyu** [[00:20:18](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1218)]
Yeah, that too.
So I will look into what's causing the issue with don't realize expand.
And I mean, that's something we long term want to fix anyway.
I think that's the most important thing.
And doing runs, making sure they are fine.
And if possible, I want to get a one or two fusion thing in.

##### **Chenyu** [[00:20:41](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1241)]
That's my plan.
And with that, let's move on to scheduler.

##### **Geohot** [[00:20:52](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1252)]
Because also, she couldn't talk on that.

##### **Chenyu** [[00:20:59](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1259)]
Oh, OK.
I think she is working on kernelize and multi-output.

##### **Geohot** [[00:21:06](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1266)]
I'll do the, for those that don't know what kernelize is.
So right now, every tensor goes through two steps.
It has a schedule step, which outputs schedule items, and then a realize step, which actually compiles those schedule items and runs them.
We're going to add a third step, where basically a schedule does two things.
Schedule groups things into kernels.
And schedule also toposorts those kernels and determines a linear order to run things in.
So we're going to separate those into separate things.
We're going to have one step, which is going to group things into kernels.
That's the grouper.
It's called kernelize.
And then a second step, which does the toposort and actually outputs the schedule item, and we'll call that scheduling.
So that's what that is.
And then multi-output is multi-output in one kernel.

##### **Chenyu** [[00:21:49](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1309)]
Let's move on to driver.

##### **Nimlgen** [[00:22:11](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1331)]
Yeah.
So for the BERT, so yeah, I'll take a look.
So actually the first slowness which is fixed, it was because of the ring reduce.
So the GPU was poorly sorted and because of that, yeah, we couldn't do ring reduce in optimal way.
And another
So it's another 15 milliseconds.
I think 10 of them is from the GPU kernels.
I'm not exactly sure why.
So actually, comparing kernels from AM and AMD, they're just different in numbers.
I mean, they're reproducible.
I mean, time is reproducible in AM, reproducible in AMD.
But yeah, they're different, some faster, some slower.

##### **Geohot** [[00:22:55](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1375)]
So that might have to do with the BEAM search.

##### **Nimlgen** [[00:22:59](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1379)]
no no i use the same one that oh it's not the BEAM okay yeah that might be the memory layout yeah uh this week i'll try to just get this kernel and try to compare them one by one and see so maybe memory layout is worse in AM um yeah um so yeah for nance i can try to so the only thing
I think, I don't know, maybe that's synchronization, but it's just basically the same like for AMD and AM.
Or maybe it's also different memory layout.
We have some page files or memory accesses.
I'm not sure we have any.

##### **Chenyu** [[00:23:50](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1430)]
Yeah.
So my impression is, I don't know if at AM.
We got some really weird, really big numbers out of a formula that doesn't make sense.
For example, we compute the accuracy and the output number is like 10 to the power of 20 or something that doesn't.
Accuracy should be between 0 and 1.
And we saw there might be some sync issue or something just completely wrong.
I don't know if that's understood.

##### **Nimlgen** [[00:24:31](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1471)]
Yeah, I think something related to that.

##### **Chenyu** [[00:24:35](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1475)]
So I think we would know more when we run the retinanets on red, because I think there the error seems to be more
obvious to see.
We'll discuss this later.
I think don't worry too much about a NaN issue.
I will try to give you a repro or at least find a way that cause the issue more consistently.
I'm doing these runs anyway.
And I think once I have something that's more reliably reproduced, you can take a look.
Speed you can already check, but for the NaN issue, I think
It's already bad enough for me to run this.
You don't need to waste time to also run that until I have a better reproducible script.

##### **Nimlgen** [[00:25:25](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1525)]
OK, yeah.
So for the USB GPU, it's currently hacking, but I got it running.
So it just can copy onto device, and it doesn't turn the GPU off.
So yeah, it's currently.

##### **Geohot** [[00:25:43](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1543)]
Wait, so it's working.
You figured out how to get around the stall as well.

##### **Nimlgen** [[00:25:49](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1549)]
Yeah.
Yeah, but it's currently. I just reset the USB connection right now.
And still, basically, I need to. Yeah.
I need to find a better way from the GPU to acknowledge the NVMe commands.
And actually they.. I figured out that they use like two.. Yeah, they actually have like two values in their controller, which is like wire to the doorbell.
So they actually like not access.. They use like this as fast path to access the doorbell.
So these registers points to the specific address which is expected and we need to have.
So yeah, I still can get this work on the GPU, but I think it's pretty close.
And I think once this works, I think I can acknowledge the request from the GPU.
But yeah, currently it works, but it's just not the.. 

##### **Geohot** [[00:27:08](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1628)]
So what do you mean, acknowledge it from the GPU?
You're going to, like, do a GPU DMA command and, like, tell it to go do something?
Like, tell it to copy something?

##### **Nimlgen** [[00:27:15](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1635)]
No, I mean, because the controller supports, like, one comment only, so it just waits for its quasi-write to be acknowledged by the NVMe.
So it can reuse this buffer later for other requests.
so and actually yeah yeah 

##### **Geohot** [[00:27:30](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1650)]
so but you're going to actually have to make the gpu do that 
you can't write to it over the usb 

##### **Nimlgen** [[00:27:44](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1664)]
um so i mean
Yeah, actually, I just try to do that.
No, I'm not.
I mean, I just try to prepare everything before and then just send comment.

##### **Geohot** [[00:28:06](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1686)]
If you want to modify the firmware to.. So the thing that I was really worried about, about modifying the firmware before, was that you were trying to add functionality.
So that's really hard.
If all you have to do in your firmware modification is patch out like one jump, I'm okay with that.

##### **Nimlgen** [[00:28:27](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1707)]
Yeah, basically just not waiting for the GPU response.
That should be enough.

##### **Geohot** [[00:28:33](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1713)]
Yeah, if that's easy.
If the thing that looks like the firmware change is a two byte change, I'm supportive of it.
Especially since we're already locked to use a single version of the firmware.
So great.
We'll use a custom firmware, make the two byte change.
But let's just not try to write functionality in the firmware because that's super hard.

##### **Nimlgen** [[00:28:54](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1734)]
Yeah.

##### **Geohot** [[00:28:59](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1739)]
But great.
And then I think..
Yeah, it should be two bytes, five bytes.
What I'm saying is not 100 bytes.
Yeah, so then it sounds like it's just going to be a whole bunch of refactoring to support whatever that DMA size is.
And then we're going to have to chunk the DMA like that, right?

##### **Nimlgen** [[00:29:26](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1766)]
I mean, we currently do the same
on using the CPU.
Oh, sure.
Yeah, we'll just have to go smaller, probably.

##### **Geohot** [[00:29:35](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1775)]
And then how long is it going to take to cold boot the GPU?

##### **Nimlgen** [[00:29:44](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1784)]
I haven't played with this.
I mean, I don't know if we can reorder some IPs.
So yeah, I haven't tried that.

##### **Geohot** [[00:29:55](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1795)]
yeah we gotta we gotta make sure that's like on the order of 15 seconds max 

##### **Nimlgen** [[00:30:05](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1805)]
yeah sounds sounds doable 

##### **Geohot** [[00:30:12](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1812)]
cool uh I mean maybe uh uuuvn says he found something on the mi300 that just loads firmware no psp required that'd be great yeah
think it's real you think it's on the gfx 11 too 

##### **Nimlgen** [[00:30:22](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1822)]
yeah yeah they do have like they have direct option to firmware um but it's when i just looked at that they have a bunch of commented code um so yeah it simply doesn't work out of the box like in their driver maybe yeah we can get this working i don't know they actually yeah for apu for apu but

##### **Geohot** [[00:30:51](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1851)]
What's APU?

##### **Nimlgen** [[00:30:54](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1854)]
I mean, when it's integrated GPU, like CPU and GPU.

##### **Geohot** [[00:30:58](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1858)]
Oh, I see.
Yeah, yeah, yeah.
Oh, so they do this for when you have the Verizon chip.
Yeah, I mean, that chip's going to have the global PSP as well.
That chip's going to have the other PSP on it.
It's going to have the CPU PSP.
I'd be super happy if we didn't have to load the PSP on our GPUs.
We should just be able to not load it, right?

##### **Nimlgen** [[00:31:35](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1895)]
Yeah.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1896)]
Yeah, that'd be great.
Well, and then also, then we can load anything we want.
You can write custom firmware on the GPU at that point.

##### **Nimlgen** [[00:31:47](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1907)]
Yeah, because currently, yeah, I just tried PSP-validated binaries.
So yeah.

##### **Geohot** [[00:31:53](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1913)]
Yeah, and custom firmware on the GPU is a lot more interesting than custom firmware on the USB thing.
I mean, who wants to deal with like an 8051 and the branch tables or whatever?
The GPU just RISKV.

##### **Nimlgen** [[00:32:02](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1922)]
Yeah.
Yeah, I can.
I know there is a bounty, but after USB, I can try that.

##### **Geohot** [[00:32:15](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1935)]
I would play with it for a couple hours.
If you don't find it in two hours, there's a bounty.
If it turns out it was just two hours, then I think it'll save you time on the USB.

##### **Chenyu** [[00:32:27](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1947)]
OK, let's move on to WebGPU.

##### **Hooved** [[00:32:42](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=1962)]
Hey, so I don't have much to say about WebGPU since last week.
I've been working on some smaller PRs involving memory that are mainly helping me learn the code base.
One of them is related to the bounty that was posted last week.
I think I fixed the issue where Viz is blocking GC of buffers.
And I added some tests.
That's in one PR.
I'll try to have that cleaned up and ready for review within a day or so.
And another PR that might save some memory,
I'm not sure it's going to be that impactful.
I'll see if there's a simple way to include it.
Otherwise, I might not.
I might just close it.
But yeah, just these things are useful for me to learn about the code base and are helping me understand.
For example, I think for WebGPU, we might define, or for exporting models,
might be a more useful way to define the buffers we want to export, just in terms of them being referenced by UOp and not being an input or output.
That might be a simpler definition than what we have now.
So yeah, that's all I've got to say.

##### **Geohot** [[00:34:06](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2046)]
Oh yeah, I'll look that PR over when it's ready.

##### **Chenyu** [[00:34:06](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2046)]
OK, retinanet.

##### **Flata** [[00:34:25](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2065)]
Hello, so I think right now the main PR has been merged, so that's step one.
Right now, I think what Chenyu said on the Retinanet channel just mainly focused on getting the TinyBox runs going, especially with FP16, because I think there's definitely inconsistent losses, one where it's NaN for the AM driver and the AMD driver.
It was going, but..
But I think we just need to make sure that it actually converges as well.
So I'm going to put up smaller PRs, just kind of add some sort of debugging flags to the main training script so that it's easier to figure out some of the issues there.
And I think when Chenyu ran the eval BEAM, I think on the last run that converged, it worked for him.
So I'll just make sure that it actually is consistent for my end as well.
And yeah, keep going on that.

##### **Chenyu** [[00:35:23](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2123)]
Yeah, I don't think eval BEAM was doing anything.
If you check the graph in my second round compared to my first round, I don't think the eval time changed at all.

##### **Flata** [[00:35:35](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2135)]
Oh, interesting.
OK, I can take a look into that for sure, because it was definitely

##### **Chenyu** [[00:35:41](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2141)]
Yeah, to reiterate what I said in the Retinanet channel, I think two things, I think, are the most important.
One is the eval speed, and another is making sure Red can run it.
So I think you can add some dev BEAM or dev run script, like we have done for ResNet and BERT.
I think that's useful for other people to reproduce the run.
And especially good if you can make empty input for the BIM run so that people can run it as a benchmark or see if it runs at all without downloading the data.
Downloading the data is like four hours of work.
Or I guess copy the data.
But making sure it's easy and we have a simple way to run benchmark, I think, helps other people to run the script and see what the issues are.
For the eval speed, for now, it's like 120% of the training time.
That's ridiculous.
I think it can be much shorter.
So check how other people's run look like, comparing their training time and eval time.
And as you mentioned, if NVIDIA has their own libraries or their way to run the eval, we should just be able to copy what they are doing.

##### **Flata** [[00:37:04](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2224)]
Yeah, I think a lot of the reference training implementations I've seen, which is pretty much based off of NVIDIA, they were pretty much using their custom implementation of it, which is parallelized PyCoco.
So if anything, we can just kind of use that as well.
But I think I'll put that as the very last thing for us to add.
But I'll definitely focus on the post-processing stuff, which is pretty much the chunk of the eval time.

##### **Chenyu** [[00:37:29](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2249)]
Also, you are saying we are doing stuff in between.
running inference and calling the pycoco tool?

##### **Flata** [[00:37:39](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2259)]
Yes, exactly.
So I think there's a function called post-process detections.
That's where basically the NumPy code is at.
So that was pretty much the biggest bottleneck there.

##### **Chenyu** [[00:37:48](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2268)]
I see.
OK, that sure sounds good.
Yeah, fix that first.
Sounds good.
OK.

##### **Chenyu** [[00:38:03](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2283)]
I see some update to the Torch front-end multi-GPU from tocubed, but I don't know if it's here.
And also, UUVN is not here.
So maybe next time I will let him know early.
B1TG, you want to say something?

##### **B1TG** [[00:38:31](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2311)]
OK.
I collected the modified AST during the BERT benchmark, and I found a few cases are slower than the AMD backend.
One is that HIP split big loop during the LLVM frontend, which will not happen in the LLVM compile stage.
The loop count can be divided by 6, not 4.
So I will optimize and not unroll the big loop.
So I temporarily add 6 to the list options to make it faster.

##### **Geohot** [[00:39:29](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2369)]
I see.
So you think that HIP is doing some unroll that is not being done with LLVM, and you can do it explicitly in LLVM using our stuff.
All right, cool.

##### **Chenyu** [[00:39:40](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2380)]
Yeah.
I think for issues like these, it would be useful if you just add some benchmark script in TinyGrad, or even as separate examples that people can run and can compare.

##### **B1TG** [[00:39:57](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2397)]
Currently, it's in my PR.

##### **Chenyu** [[00:40:03](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2403)]
I see.
There is a benchmark script.
Should I push the collected functions to the repo?

##### **Geohot** [[00:40:21](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2421)]
Which PR are you talking about?
What number?
I don't see a PR here from you.
One speed PR.
Oh, there we go.
I got it.
Cool.

##### **B1TG** [[00:40:49](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2449)]
And there are another functions that have many add and multi ops.
It's like a thousand lines of LLVM IR code.
The HIP reorder those options to make it faster.
I still figure out why it happened.

##### **Geohot** [[00:41:28](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2488)]
Yeah, I see where you added the splits to the hand-coded optimization stuff.
I mean, I'm really interested in why things are slower after BEAM.

##### **B1TG** [[00:41:42](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2502)]
And after add 6 to the split option, the AMD backend also gets speed up.

##### **Geohot** [[00:41:54](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2514)]
Yeah, but again, so this is like all the hand-coded optimization stuff is not what happens when things are beaming.
The thing that I'm most interested about is BEAM equals two speed.
Hand-coded optimizations are just kind of luck whether they're good or not.

##### **B1TG** [[00:42:10](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2530)]
I'm not tested with a BEAM.

##### **Geohot** [[00:42:13](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2533)]
Yeah, see, the BEAM thing is the fundamental thing I care about.
Yeah, you should be able to just, I think this script approach is a good idea.
It's the same one we have for the PTX and CUDA.
Yeah, so just throw BEAM equals 2 on there and see how things are going.
And if you find ones that BEAM to something slower, then figure out what's missing.

##### **Chenyu** [[00:42:34](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2554)]
Sounds good.
OK.
That's it.

##### **Geohot** [[00:42:49](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2569)]
I could say a little stuff about the cloud.
I mean, this buffer change looks good.
I don't really know why I didn't do it.
Probably for some image crap.
So that can go.
And then, yeah, Cloud Graph.
Yeah, it's a lot of lines.
I don't know.
Cloud Graph kind of points to this what really is graph.
I don't know.
Maybe I should just merge it, and we can refactor it later.
A cloud graph is kind of the idealized graph from the 9876.

##### **Geohot** [[00:43:35](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2615)]
Yeah, I don't know about that, but definitely the buffer one is a good place to start, and I like that.
UUVN's looking at cloud, because cloud is how we're going to support scale out.
I also just merged the fast pattern matcher.
I don't know what's wrong with the setup environment thing, why that keeps breaking, why that's so slow.
But everything else looks good.
Everything else looks faster.
I mean, we traded off some lines and some startup time for Python speed.

##### **Chenyu** [[00:44:20](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2660)]
I also tested MOE.
I think MOE on master, for some reason, is 10% faster than that PR.
So try sync and see.
I think with Fuse Arange embedding and the Fuse ARange change in that gets like 40%.

##### **Geohot** [[00:44:52](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2692)]
Cool.
Yeah, I've made a new channel, the general ML channel.
It's for TinyGrad developers if you want to talk about
just any general machine learning stuff, high-level technical stuff only.
But yeah, this Apple paper is wild.
The MOE models scale differently from other models.
And they seem to be like, my understanding of that paper says that MOE is way more data efficient than non-MOE.
I'm like, yeah, you can kind of imagine why.
Good that it's kept after.
For other bounties,
If someone can get, oh, by the way, please, if you are submitting a PR that you did with AI and you don't understand the PR, don't waste anybody's time.
I'm not an idiot.
You're just wasting my time.
You're wasting your time.
You're wasting everybody's time.
I'm not saying don't use AI.
I'm saying if you use AI and get something you do not understand, I do understand it and you look like a clown.
So yeah, and that's generally true for people who use AI for other stuff too, so.
just general general, please don't use AI unless you know what you're doing.
So for open bounties, $500 if someone can get flash attention to work, it kind of works.
All the infrastructure is there for it now.
I think it's doable in a few days work.
If someone could figure out how to run unsigned firmware on the 7800 XTX, it was discussed a little in this meeting.
A whole bunch of Torch backend stuff still.
There's four of them up there, if anyone can do them.
Oh, the GC one, I will lock that to Hooved, if there's been good progress there.

##### **Geohot** [[00:47:12](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2832)]
If someone wants to get Llama4 Scout running once we have MOE stuff, $500.
The CPU graph one, I know there's a PR for that, but I think I closed it this morning.
Please read your PR.
If you are copying and pasting stuff tons of times, even in the test, please refactor it.
$300 if someone can get 5090 support in the NV backend.
I think you basically just have to add one class.
You have to add one data type for the launch struct, so it's not going to be too hard.

##### **Chenyu** [[00:47:44](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2864)]
I think the difficulty in that is to get a 5090 first.

##### **Geohot** [[00:47:48](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2868)]
Yes, exactly.
We also have, did anyone get the tensor cores for RDNA 4?
Oh, I see this is locked to B1TG.
Is that, I don't know why it's draft.
But yeah, then we'll leave.

##### **B1TG** [[00:48:14](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2894)]
Oh, I have finished in this week.

##### **Geohot** [[00:48:17](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2897)]
Cool.
Sounds good.
Yeah, that's a lot to you.
I knew it was like a line or two.
I don't know why this.
Oh, I see why there's a lot of changes.
But yeah, it's just like some boilerplate and then one basic line.
Cool.

##### **Chenyu** [[00:48:29](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2909)]
Oh, I will comment on the FP8 one.
I see the author opened a new one.
I don't know.
I think it's possible to split that into smaller PRs and making sure there's no bug.
I think you can add the FP8 Dtype and making sure any great stuff without really computing those Dtypes or handling those type promotion correctly.
and add the support to that to the thing, something like that.

##### **Geohot** [[00:49:13](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2953)]
I think that sounds good.
It's too big, and that's what happened last time, yeah.

##### **Chenyu** [[00:49:17](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2957)]
Yeah, and everything added should, in some way or another, be testable.
I think last time there was a Python backend test thing.
I asked why it was not tested, and the author says tested.
I was like, OK.

##### **Geohot** [[00:49:33](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=2973)]
Last time, the tests weren't even running.
The two tests were called, and they just weren't running because actual CUDA is not installed.
So yeah.
And then on CUDA, they didn't even work.
So yeah, I want to see a lot more rigor around that PR in order to get it merged.
I always felt iffy about it.
It's not FP8 in general.
I'm actually very excited about FP8, but I think it's the general quality of that PR that needs to be broken up into.

##### **Chenyu** [[00:50:02](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3002)]
Yeah.
I think the author's here.
I will comment on that PR directly later.
And the Z3 stuff as Sied Lykkles will be ready by tomorrow.
OK, great.
We have more pieces that render part of a tinygrad into something else.
It's like the fast matcher is rendered into itself.
And this S3 render into S3 statements there.

##### **Geohot** [[00:50:59](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3059)]
Yeah, the rendering into itself is fun.
I'm using the PatternMatcher in order to create PatternMatchers.

##### **Chenyu** [[00:51:10](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3070)]
Yeah, that's a little bit like how Compiler works.

##### **Geohot** [[00:51:14](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3074)]
Yeah, we have a great general API for it.
The worst hack that I put in is I use CmpNE to mean CmpEQ.
Maybe we should just add a CmpEQ op.
Mm-hmm.
Yeah, but then you add it to binary, things get slower.

##### **Chenyu** [[00:51:35](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3095)]
I don't know.
OK, whatever.

##### **Geohot** [[00:51:41](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3101)]
Everybody can enjoy.
It looks like pretty much a 30% speed up for compilation.
And it also looks like a 5% speed up for everything.
So running, even, looks 5% faster.
You can see it in the benchmarks.

##### **Chenyu** [[00:51:55](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3115)]
Great.
I already started a test run for it.

##### **Geohot** [[00:52:00](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3120)]
Cool.
It passed process replay, so there should be zero changes, but you don't find anything.

##### **Chenyu** [[00:52:10](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3130)]
Oh, that sounds good.
OK.
Anything else?

##### **Geohot** [[00:52:17](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3137)]
No.
More speed this week.
I'm going to get that.
I'm going to get that external benchmark schedule under 500 milliseconds.
So we'll get an actual full 2x.
Across TinyGrad.

##### **Chenyu** [[00:52:37](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3157)]
Cool.
Yeah, I think that's it for this meeting.
Making good progress.
I think we can do a release maybe in two weeks after we are ready for MLPerf.
The speed looks nice.

##### **Geohot** [[00:52:54](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3174)]
Do a what in two weeks?
Oh, do a release?
Yeah.

##### **Chenyu** [[00:53:00](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3180)]
And I think that's it for this meeting.
Thanks, everyone and see you next week.

##### **Geohot** [[00:53:06](https://www.youtube.com/watch?v=4p_uWDeaO_8&t=3186)]
Bye

