# 2025-04-07 Meeting

### Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time)
- company update
- fast python, softmax
- bert, mlperf
- scheduler
- driver
- tensor core / local
- onnx, moe speed
- webgpu
- retinanet
- torch frontend
- fast div / mod stuff
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=BQQqrUqe1VA)

### Highlights

Coming!

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=0)]
Let's start with company update.

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=7)]
Yeah, so the main thing is the Tiny Box Green is postponed.
Pre-orders are just like the Nintendo Switch due to the evolving tariff situation in the United States.
Basically, if the tariffs actually stay at anything near the levels that's been stated, we are just no longer profitable.
So I'm not going to make these boxes at a loss.
We have two basic options.
So we've been reached, our motherboard supplier and GPU supplier both reached out saying, we're going to update you on tariffs this week.
So we'll learn some stuff.
We have two basic options.
Either we can all pray that the tariffs will go away, or we can move production to Hong Kong.
And then most of our, like 40% of our orders are international.
So yeah, we'd just be able, Hong Kong is fully free trade.
We'd just be able to ship it from here.
Assuming we can ship 5090s here, which is a whole other thing.
What's considered China and what's not considered China.
So yeah, that's the main company update there.

##### **Chenyu** [[00:01:17](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=77)]
Great.
Any update for the contract?

##### **Geohot** [[00:01:25](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=85)]
Oh, yeah.
They said Friday.
They said they'd review it by Friday.

##### **Chenyu** [[00:01:31](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=91)]
Great.

##### **Geohot** [[00:01:32](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=92)]
Yeah, I think we should be good.
It's a little bit annoying to actually run the DSP, because you have to get this signed thing.
But that was pre-negotiated.
So we'll make it work.

##### **Chenyu** [[00:01:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=105)]
Great.
OK.
Company update, let's move on to specific projects.
Want to talk about stuff?

##### **Geohot** [[00:01:57](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=117)]
So fast Python is very much doable by someone externally.
PR 9737, someone else can totally do this.
There's already $3,000 of bounties on the table to do it.
You just basically need to write a codegen
for UPats that generate tight code without function calls without lots of like the minimum number of branching the minimum number of dictionary sets.
And I think you can get pretty easily a 4x speed up to $2,000.
And if you push it a little further, you can get an 8x speed up.
Yeah, so, like, you know, I don't know why these sort of bounties don't get claimed.
Like, this isn't hard.
I know there was talk about using, oh, tree automata or any of this stuff.
You don't need any of this.
Just, like, look at the match function and then get the match function compiled.
Like, start there.
Because right now it's doing, yeah, like, Python function calls when it should just be really a big if statement with a few clauses maybe.
But then the clauses can all be made explicit.
You can look at the branching of the UPats.
We could have like a UPat optimizer.
I was even thinking if you really want to go crazy with this, you could write a UPAT in UOPs and then optimize the UOPs to be the matcher.
You know, reuse all our match logic for that.
But yeah.
So I'm hoping someone picks that one up this week and I can work on Softmax.
which I think is very doable.
I think I could very doably finish Softmax in the next two weeks.
That's single kernel Softmax, not three kernel Softmax.
I see the path to do it.
It's a simple scheduler change, too.
It's really just all work on codegen and all the crap in kernel.py.

##### **Chenyu** [[00:03:50](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=230)]
Is there a branch I can test?

##### **Geohot** [[00:03:53](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=233)]
Oh, no, not yet.
No.
I'll have a branch by the end of this week.
Yeah, so the problem is the new dimension, like the reduced dimension on the softmax, is both a reduced dimension and an output dimension.
And we don't have any real way of expressing that.

##### **Chenyu** [[00:04:15](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=255)]
Yeah, so you're something real, first real reduce, something like that?
Yeah, so... You use shape to be different to know which one is reduced and stuff.

##### **Geohot** [[00:04:29](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=269)]
Yeah, that's potentially one way to do it.
Another way to do it, which I'm thinking about that might be easier to not have to change kernel.py, is just to create two identical axes.
There's no reason at all I can't make a shape be like 32, 1, 1 as the strides.
I know that's the reduce access.
I think that'll be better.
But I don't know.
I was just playing with it tonight.
So I don't know exactly how I'm going to do it yet.
I'll have a branch review by the end of the week.

##### **Chenyu** [[00:05:03](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=303)]
OK.
Sounds good.
OK.
So the whole reason we start this discussion for making softmax fast is
We have about realistically, maybe a little bit more of like two weeks of dev time to make BERT fast.
And after that, I need to make a real run and the submissions.
The deadline is May 2nd, but we want to making sure everything is correct.
Given this time we are also using our AM driver.
We really need to make sure we can back to back run those for like five times without hanging.
So this time, we will submit BERT, TinyBox Green, TinyBox Red.
We submit these two last cycle as well.
And this time, we are also planning to submit with our great 8xMI300x machine.
So I am making the script change to do all the MLPerf logging.
Looks fine.
I was testing earlier, and for some reason, if I don't print debug equals to 2, the machine will hand consistently.
So I will push the script, and maybe someone can take a look why it's hang.
Yeah, so we look at how our speed compare with other submission, especially with H100s.
turns out other than maybe flash attention, our softmax is really bad.
So that was kind of a reason why we're working on softmax.
So the greatest change I made today is I have this realization that
for setup, because setup time is separate.
And for the setup, we really need to only do a vert layer equals to 2.
We don't need to do 24, because kernels are the same.
We only need to beam them once.
So we can save five minutes setup time, and we can potentially search a lot more.
So I was pretty happy about that.
So we know if we search beam equals to 32,
It's 5% faster, so the potential is there.
But that takes about two hours to search.
We only have 30 minutes.
So it's a combination of finding the kernel and actions that makes that 5% and have a BEAM setup so that we can search that kernel within 30 minutes limit.

##### **Geohot** [[00:07:52](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=472)]
So layers equals two actually gets every kernel?

##### **Chenyu** [[00:07:57](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=477)]
Yeah, it's the same kernel for 24 layers.
Cool.
I think layer equals to 1 also works, but whatever.
2 is good.
Yeah, 2 is the one we use in benchmark 2.
Yeah.

##### **Geohot** [[00:08:12](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=492)]
It's really cool that that gets all the kernels.

##### **Chenyu** [[00:08:16](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=496)]
Yeah, so it's basic.
I was like, is this too much for MLPerf?
But this is really similar to we schedule everything, and we store the unique kernel, and we BEAM through those unique kernel.
I think this is fine.
Yeah, so with that, we save five minutes.
So previously, the setup time is 24 minutes.
Now it's 18.
So with that, and search more.

##### **Geohot** [[00:08:51](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=531)]
Great.

##### **Chenyu** [[00:08:52](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=532)]
Yeah.
And so I think between the parameter and potential savings in embedding with FUSE_ARANGE, there's probably like end.
like split, reduce up, some small, like 1%, 2%.
There are maybe up to 10% of saving from these tuning.
I don't know how much Softmax will get.
We will know better maybe at the end of this week to have an estimation for timing.
I'll probably do some tuning when we get closer to the submission time.
It's better to do tuning when things are fast.
So hopefully with reasonable conversions, we'll get better timing.
Yeah, that's the plan.
And with that, let's move on to, I should call this grouper scheduler, but let's move on to scheduler.

##### **Qazalin** [[00:09:54](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=594)]
I mean, they have grouper.py.
So, yeah.
I think on I merged grouper.py, basically separating the concerns between creating the kernels versus linearizing those kernels, ordering them such that we then run this
kernels in that order.
So it separates the two problems.
I know George last week worked a little bit on reordering the copies in multi.
So now I can do it because it's totally a separate part.
It's the thing we talked about with the scheduler returning becomes map and then later creating the kernels, creating the schedule items.

##### **Geohot** [[00:10:47](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=647)]
Yeah, so I see what you're doing.
Sorry, go ahead.
Oh, I see what you're doing here with get becomes map.
Can you actually return that all the way to the, I mean, ideally I want to call the group from tensor.py.

##### **Qazalin** [[00:11:12](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=672)]
Yeah.
I see what you're saying?

##### **Geohot** [[00:11:17](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=677)]
Like we should rewrite the graph and then have the toposort be another step.
And it can be called from schedule.
The semantics of schedule shouldn't change, but maybe you have another one called pre-schedule or something, or group.

##### **Qazalin** [[00:11:41](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=701)]
I think that's the idea, yeah.
Group into kernels.

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=705)]
Yeah, group into kernels.
And it can be kind of a hidden method, but it should be on tensor.py, and then it should rewrite all the tensors that just have kernels in their history.

##### **Qazalin** [[00:11:55](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=715)]
Yeah, yeah, yeah.
I think this is towards that.
But yeah, we want to move on to three stages, basically.
Group, linearize, and exec.

##### **Geohot** [[00:12:10](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=730)]
Yes.
And yeah, notably, I mean, the term linearize is overloaded.
It's the same thing, really.
And we also use linearize for codegen, but it's really the same problem.

##### **Qazalin** [[00:12:34](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=754)]
Yeah, so this is going to be for the rest of this week.
I'm going to work on grouper.py, cleaning things up and setting the infrastructure so that once we have softmax, I can add the expand axis up into the scheduler and will help on kernel softmax, hopefully.

##### **Qazalin** [[00:12:54](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=774)]
I'll also touch briefly.
Yeah, go ahead.

##### **Geohot** [[00:13:04](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=784)]
I think the scheduler change is actually pretty simple.
You just have to occasionally rewrite views in some special set of cases to be expanded axis.
And I think it's pretty easy to detect the cases, too.

##### **Qazalin** [[00:13:18](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=798)]
Yeah, you're right.
I think my big thing is just going to be on making sure that the transfers are mapped correctly in the graph.
we have contiguous in the graph.
So today, we were looking at the softmax kernel, and it wasn't really obvious from viz.
When things are being realized, I want to make that very explicit, like the decision.
Yeah.

##### **Chenyu** [[00:13:43](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=823)]
Next, driver.

##### **Nimlgen** [[00:14:00](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=840)]
yeah so um so this week i'm just going to continue working on the gpus bgpu so i tried like we discussed two approaches so one is just pretending being NVMe and the second is just try to
Just try to do writes with, like, set all the USB registers and memory map to join to write.
So I tried this this weekend, and I got nothing.

##### **Geohot** [[00:14:37](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=877)]
With the registers.

##### **Nimlgen** [[00:14:39](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=879)]
Yeah, I think I have a feeling that, like, we need...
We need to set more than two registers, and each write will just overwrite more than two registers we need.
So it's kind of without firmware changes.

##### **Geohot** [[00:14:59](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=899)]
Yeah.
So how about pretending to be an NVMe?

##### **Nimlgen** [[00:15:04](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=904)]
Yeah.
So yeah, I started this today.
So yeah.
I think this is closer to be done, and that sounds simpler.
So the only thing we have, we still have is that it just reset the controller after the write, because it doesn't like the GPU being in NVMe.
So yeah, that's the only problem.

##### **Geohot** [[00:15:30](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=930)]
Great.
This approach is good.
Let's just push this through.
Let's just make it work however we can.
Do we have a way to update the firmware?
Because I think if you do the NVMe approach, it's only going to work with one version of the firmware.

##### **Nimlgen** [[00:15:49](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=949)]
Yeah.
Yeah, we can do that.

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=955)]
As long as you have a script to install it, it's totally fine.
Great.
Yeah.
I don't know.
I was excited about the USB registers, but you're right.
I tried it for a bit.
I didn't make any progress either.
So who knows?
Yeah.
Maybe I can NVMe and reset the firmware and just figure out a way to flash the firmware to the one that we know how to poke and make happy.
Also, did you look at the AMD hardware?
Did you look at the sync stuff at all?

##### **Nimlgen** [[00:16:44](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1004)]
What sync stuff?
Mi300X?

##### **Geohot** [[00:16:48](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1008)]
Mi300X, yeah.

##### **Nimlgen** [[00:16:51](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1011)]
Not really.
I don't spend much time.
Just chat and all this information.
I just haven't tried anything.

##### **Geohot** [[00:17:00](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1020)]
Yeah, so I think that maybe the thing to try, just like briefly try it only if it's easy, is packet 99 is AQL packet.
So I wonder if I don't want to switch to AQL entirely, I don't want to set up AQL queues, that sounds annoying.
But I wonder if we can just change our dispatch to be an AQL command.
And it looks like built into the AQL command is where they're doing the sync.
Like, they check a bunch of AQL config registers, and then if the AQL config registers are happy, it does a sync.

##### **Nimlgen** [[00:17:38](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1058)]
Yeah, I can try this today, yeah.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1062)]
Yeah, only if it's easy.
I think that, like, I mean, I don't think AMD is going to help us with it.
I don't think they have any idea.
I'm starting to think that all this firmware is coded in assembly.
So yeah, I don't think we're going to get help.
If we can keep the PM4 and we can just... Or the other thing we could potentially even do is just do an AQL packet that is like an empty AQL packet.
That's probably the ideal thing to do.
If it's an empty AQL packet and it could trigger the sync, and it could just be like packet 99, AQL packet, trigger sync, don't actually run a kernel, that's great.
Then we have a sync packet.
But yeah, they're doing something that looks not to be memory.
They're doing something that looks like some secret communication between the MECs.

##### **Nimlgen** [[00:18:26](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1106)]
Yeah, OK.
Yeah, I can try this.

##### **Chenyu** [[00:18:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1125)]
Cool.
OK, next we have tensor core slash loco.

##### **Ignaciosica** [[00:18:52](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1132)]
Hi.
Well, I finally made some progress on the LDS, at least on the correctness side.
I still haven't addressed much of the speed.
Like this Naive implementation won't make it any faster for small matmuls, because I think in that case,
the hit rate for the cache is already pretty good.
So using the locals in some cases isn't going to make it faster.
And I'm afraid that that's the case for the BERT ones, that they are fairly small matmuls.
So yeah.

##### **Geohot** [[00:19:37](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1177)]
So we haven't actually done the thing that's going to make locals faster yet.
So I see your pull request, and I see a comment about, so you're saying this doesn't apply?
Yeah, you can get nones in real strides without using padto.
Try it on convolutions.

##### **Ignaciosica** [[00:19:57](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1197)]
Yeah.
On convolutions, if the pad is 1 in the convolution, it works.

##### **Geohot** [[00:20:04](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1204)]
No, but you can try other things in convolutions where you'll end up with real strides of none.

##### **Ignaciosica** [[00:20:11](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1211)]
Yeah.

##### **Geohot** [[00:20:12](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1212)]
You can't just check to see if pad 2 is in the thing.
You have to actually, if you want to gate on real strides, you actually have to gate on real strides.

##### **Ignaciosica** [[00:20:21](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1221)]
Sure.

##### **Geohot** [[00:20:22](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1222)]
Which is fine, but you should have the same check when you're applying it, when you're doing apply LDS and when you can call the optop.

##### **Ignaciosica** [[00:20:30](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1230)]
Okay.
Sure, I should...
Sure, go ahead.

##### **Geohot** [[00:20:39](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1239)]
Yeah, just make sure, because you can trigger that in a lot of ways beside padto.
Does this work with loads and stores?

##### **Ignaciosica** [[00:20:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1245)]
Yeah.

##### **Geohot** [[00:20:47](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1247)]
Cool.

##### **Geohot** [[00:20:49](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1249)]
So the thing that's really going to make it fast, even before we get to the other two opt-ops, is whenever you have a global load followed by a local store,
there are special instructions that can do that asynchronously.
At least, I know the NVIDIA GPUs have these.
So that would just be a rewrite rule in Cstyle, in the CUDA renderer, that says to do this fast thing.
So you might be able to get speed already with this.
I think it's worth trying.

##### **Ignaciosica** [[00:21:25](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1285)]
OK, I'll take a look at that.
And I think that's basically what's happening for the matmul I make.
Actually, it shouldn't make it faster, as it only loads into local and then stores from that into the globals.
But I think that once that is issued, the compiler actually leaves the thread alone, liberates the thread, and it sends that to make asynchronously.
And that's why it makes it faster, because if it was

##### **Ignaciosica** [[00:22:05](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1325)]
Like basically the... Sorry.

##### **Geohot** [[00:22:08](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1328)]
You can look to see if it's doing anything like that, but I'd be surprised by it.
I'll link the instructions in the NVIDIA hardware channel.
They're called... There's like bulk copy and non-bulk copy.
So I would be surprised if the compiler is capable of inferring that, but you can check.

##### **Ignaciosica** [[00:22:26](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1346)]
Yeah.
Not for NVIDIA.
I tested it in my Mac, and it did so, but...

##### **Geohot** [[00:22:35](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1355)]
Oh, the Mac's doing it.

##### **Ignaciosica** [[00:22:37](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1357)]
Yeah.
It shouldn't be faster, because it has the same access to Globals.
But it only goes through Locals, and it's way faster.

##### **Geohot** [[00:22:51](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1371)]
Cool.

##### **Ignaciosica** [[00:22:51](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1371)]
That was the example of speed that I mentioned in the PR itself.
But yeah.
And one problem I had.
Thinking through that, through this asynchronous copy, I think it's going to be a search problem, making it the thread pattern and the local layout.
Because right now, our search algorithm is greedy.
And if you

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1405)]
I wouldn't worry about any of that.
I would get correctness work first.
And then you can totally get the async stuff to work without having to worry about the thread pattern.
Don't use the bulk one.
If you use the non-bulk one, you don't even have to think about that.

##### **Chenyu** [[00:23:38](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1418)]
Yeah, I think search, we can work separately once you say, OK, this is a kernel.
This is a few steps of actions that needs to be applied for it to be fast.
We can either make that a big action, or we just write a better search.
So don't worry about that.

##### **Geohot** [[00:23:58](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1438)]
We should also manually find these before we try search.
We should be able to manually on AMD get much more.
Yeah.

##### **Chenyu** [[00:24:06](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1446)]
So you need to have the kernel, the raw AST, and you say, OK, this is the sequence of action.
If the searcher finds it, it will be fast.
So we first verify the solution is in the space, and we improve the searcher to find the solution.

##### **Ignaciosica** [[00:24:24](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1464)]
Yeah.
For Mac, I manually searched.
And yeah, it needed a whole bunch of sequence in order to make it look like.
not regressed.
So yeah.

##### **Chenyu** [[00:24:39](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1479)]
No, I mean, that's also a good problem for researchers to have, right?
We know the search for this is not going to be smooth because of our instructions like this.
So having this as an example, it's a motivation for us to make search better.
Yeah.

##### **Chenyu** [[00:25:01](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1501)]
Cool.
OK.
Sorry, go ahead.

##### **Ignaciosica** [[00:25:05](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1505)]
No, no.
That's it for me.
One minor thing is that a shared memory used in PTX is broken.
And I don't know if that gates the PR or not.

##### **Geohot** [[00:25:23](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1523)]
Absolutely it gates the PR, yeah.

##### **Ignaciosica** [[00:25:26](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1526)]
OK.
So I'll try to find what's happening there.

##### **Chenyu** [[00:25:26](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1526)]
Cool.
Moving on to ONNX.

##### **Zibokapi** [[00:25:40](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1540)]
Hi.
Hello.
OK.
So I had a pretty brutal week.
I found a lot of holes in my knowledge about Pattern Matcher, Kernel, and UOps
So for ONNX, pushing the half cast right, there are two main problems I encountered for that.
The first one being, I don't think our pattern matching infrastructure supports
Because it goes from a reduced axis, in between a reduced axis and a store.
And in between, we want to push the cast rightward when it has a chain of ALUs and a cast.
I don't think we can exactly get that pattern and match it directly.
We have to slice and do it incrementally in steps.
But doing it in steps,
The thing I'm afraid of is there are maybe unintended consequences to that, because we don't have- 

##### **Geohot** [[00:26:56](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1616)]
Wait, wait, wait, wait.
What's the pattern?

##### **Zibokapi** [[00:26:56](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1616)]
The pattern is a reduced axis and a store.
And in between, it's chains of ALUs and, sorry, reduced axis, cast half, and ALUs and store.

##### **Geohot** [[00:26:56](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1616)]
Yeah.
This is a one-line pattern match.
You want to push that cast down through the chain of ALUs all the way to the store?
This is one line.

##### **Zibokapi** [[00:27:03](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1623)]
Okay, so our pattern matcher supports describing that chain of ALUs.
Okay.

##### **Geohot** [[00:27:12](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1632)]
You have to do them one at a time.
No, it does it one at a time, right?
You say that I have an ALU and a source that ALU is a cast, and then it puts the cast on the other side of the ALU.

##### **Zibokapi** [[00:27:23](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1643)]
But how do we know between a reduced axis and a source?

##### **Geohot** [[00:27:30](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1650)]
You don't.
But why do you care?

##### **Zibokapi** [[00:27:32](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1652)]
So then we push anywhere that there's a cast to have and an ALU afterwards.
Is that correct?

##### **Geohot** [[00:27:40](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1660)]
Yeah.

##### **Zibokapi** [[00:27:41](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1661)]
OK.
Yeah, so I tried this for OpenPilot.
It works, and things are good.
I think if I were to get this merged, I will have to add more tests around this, because the first time I tried it, I forced the pattern just to get the cast all the way to the store.
And then the patterns were intentionally wrong, but CI still passed.
So I think I need to, because if you want to use this generally, there needs to be more tests around this.
And I still haven't written the tests.
Anyways, that's for the ONNX thing.
Next for OLMOE, I found that the indexing part is actually pretty efficient after the kernel has been BEAMed.
Sometimes before the beam search, the first kernel that comes out, there's a lot of redundancy in how it's done.
But after BEAM, it's already pretty good.
I don't think I can improve that anymore.
So the other thing is the topK implementation.
But the topK implementation, it's not doing sorting for a huge thing.
It's only 64, and we're just gathering the top eight.
So I think even if I improve that, there's not going to be too much time saved.
Chenyu also suggested that I might have to find some FUSE_ARANGE usage outside of the getitem after the top k, maybe embedding or something.
So I have to look into that.

##### **Chenyu** [[00:29:23](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1763)]
Yeah, so I think specifically for MOE, since I think we are going to have more MOE problems down the road.
Now Lama is also on MOE.
First, just check how many weights are we really reading, or what's the total memory access we are doing to make sure
Because a lot of these reading the things we don't need, either it's like embeddings or MOE itself, because the tricks we use with ARange, it's very likely like accidentally just loads everything and have a lot of zeros here and there.
So I think it's good to establish that we are not reading anything dumb.
And that's basically also how we calculate the upper bound for how fast this thing can be.
And for a bound T, it's like 50%, so like a 2x overhead for your other element-wise stuff.
So making sure that's right, then see where the bottleneck is.

##### **Geohot** [[00:30:39](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1839)]
You already have this already tracked.
In global counters, there's something called global mem.
And you can just see the total amount of memory that's being read per token.

##### **Zibokapi** [[00:30:49](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1849)]
OK.
Yeah, I'll check that out.

##### **Chenyu** [[00:31:00](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1860)]
OK.
Sounds good.
Let's move on to WebGPU.

##### **Hooved** [[00:31:10](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=1870)]
So
based on ChenYu's advice last week to study the memory planner because of its concerns being somewhat related to what we were talking about with model export.
I did that, and I think
that I've learned some things that, as a result, maybe we could simplify the logic for model export.
And it's related to the bugs or the things that are claimed to be bugs that I wrote about in the Discord with the memory planner and how it's optimizing buffers and also related to that bounty that was just posted.
But yeah, there's some issues there.
I mean, potentially after fixing the issues, the logic for deciding what buffers should be exported could be simpler in terms of it could just be as simple as only buffers that are realized after scheduling.
which is a bit simpler than buffers that are read from before they're written to.
So yeah, just working on that.
Also, I added types to the WebGPU runtime, and WPMed wants to review them separately out of the current PR.
So I'll open a new PR for that.
And yeah.
Yeah, I wanted to make sure I fully understood what we discussed last week with, you know, the scope of the refactor.
And so I, you know, I read up on the, you know, I tried to make sure I understood, like, the kernel graph and all that.
And I agree that, you know, the most elegant
solution here for exporting the model would be a graph rewrite on the kernel graph.
But I also agree with the conclusion from last week, which is that the scope of that root factor is maybe too big for now.
But I do think this is on the way to that.
So let me know if you have any questions.

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2004)]
Sounds good.
Yeah, I put the bounty up for the memory planner thing.
I'm happy to do more.
some bounties like that, as they come up as you find bugs, I'm always happy, pretty much if you like ever find something that's like a real bug, I'm always down to put like $200 on a bug fix, like for something that's like fundamental, you know, if someone finds a bug and like, Oh, well, if I use this thing with these parameters, and like, no, you can fix that bug.
But yeah, if you ever find fundamental bugs like that, I'll throw bounties up.
And I think that's a really good way to understand the code base.

##### **Hooved** [[00:33:56](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2036)]
Yeah, I'll try to substantiate it like Nimlgen asked for with some simple tests.

##### **Chenyu** [[00:34:09](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2049)]
And yeah, type change or small refactors, always good to have those as a small separate PR.
And you can use process replay to making sure it's a true refactor.
Basically, if you are working on a pretty big project like this one, it's always good to separately small things and have them merge into a master.
So after you rebase, your diff becomes smaller so that you don't have a very big PR that you need to keep track of all the small things you add.

##### **Hooved** [[00:34:50](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2090)]
Right, yeah, I think the types are kind of a no-brainer thing that I can do that for.
Some of the other stuff, like the reason I haven't done that, like with the graph runner and stuff, is I'm just not sure that I want that to stick long term.
Or I am, but I'm just not sure I want it in that form.
So I just haven't PR'd that stuff yet.

##### **Chenyu** [[00:35:11](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2111)]
Yeah, that's perfectly fine.
First, making sure you go through everything and have the whole picture in mind.
Cool.
Sounds good.
With that said, let's move on to RetinaNet.

##### **Flata** [[00:35:28](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2128)]
Hello.
So I've been able to actually get a good training run for RetinaNet on float16 that is actually not rounding up the metric.
So it's definitely above the 0.34 metric.
So there's that.
I'm just trying one more run with a higher batch size.
And I'll try to reset the... Or not resetting the JIT cache, but it's actually not working.
Like, it's still running out of memory, so I just kind of foregone on that for now.
But I think I should have a command for you, Chen Yu, this week to...
uh repro it and i think i'll probably put one more pr i think just kind of moving some helpers uh that's uh that was in the mask rcnn and uh repo but i'll just kind of or a model file and just moving it into the helpers on under ml perf and then i think that should be it

##### **Chenyu** [[00:36:25](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2185)]
oh sounds good
At this point, you are the person that's most familiar with that.
So if you think moving those helpers is helpful, by all means do that.
I was checking your runs, and I saw you were using 156, and it was 126 before.

##### **Flata** [[00:36:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2205)]
Yeah, that's the one that, so I think the last time I posted, I forgot to just update that message.
The one where it increases to 156, I think after the first eval went through, so after the first epoch and then after the first eval finished, I think after like 15 steps, it stopped going through.
And I don't know what's happening.
And it happened earlier last time as well.
So I don't know if it's the eval batch size that kind of caused it as well.
But that's why I reduced the eval batch size.

##### **Chenyu** [[00:37:13](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2233)]
How did you pick that size?
Is it just a large fit?
Because I'm asking because I would have thought 144 sounds like a better number than 156.
So you have 24 on each GPU instead of 26?

##### **Flata** [[00:37:29](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2249)]
Yeah, I just went up as much as I can.
I don't think the 156 is actually the max yet.
I've reached where it's actually running out of memory.
But I can try a different number.

##### **Chenyu** [[00:37:44](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2264)]
So usually, GPU is designed to be good for multiple of 32.
But if you cannot make it 32, 16 is good.
That's why BERT or 96 is pretty nice.
You have 16 on each device.
Then if you cannot make it 16, make it a multiple of 8.
So that's why 144 might be better, because it's 24 on each device.
That's kind of how I try this.
I don't know.
It might be faster.
So when you are being this stuff, just have that in mind.

##### **Flata** [[00:38:23](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2303)]
OK.
Sounds good.

##### **Chenyu** [[00:38:25](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2305)]
Cool.
Yeah.
Once you just give me the command, I will reproduce.
And you also say that next cycle, we will still have RetinaNet for MLPerf, it seems like.
So if you are interested to make the thing good and submittable, you have another cycle to work on that.

##### **Flata** [[00:38:49](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2329)]
Yeah, that's my plan.
So I think after, I guess, the first half of it is done, I'll definitely focus on the eval for sure and making the BEAM search much faster.
Because I think around 35 minutes, I think, when it's searching.
So I think that could be optimized further.
So I'll take a look into those.

##### **Chenyu** [[00:39:06](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2346)]
Yeah, if we want to submit, definitely eval is a big part of it.
I think for now, it's still taking half of our time.

##### **Geohot** [[00:39:14](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2354)]
Yeah, once we, by the way, once you merge this, if you get under 24 hours, the bounty is yours.
But then, yeah, double the bounty by actually getting on MLPerf next time.

##### **Chenyu** [[00:39:24](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2364)]
Sounds good.
Great progress.
Oh, I don't know if I just put torch frontend, but I don't really see like a real progress.
Oh.
You want to talk about the fastdiv and mod?
So I merged the fastdiv.
I think it's pretty cool.
And if you are interested in working on using the, I saw your Z3 for fuzzing symbolic.
If you want to, as part of the fast mod, if you want to also update the validate index to use Z3, we can put a bounty for that.

##### **Sied Lykles** [[00:40:17](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2417)]
Yeah, I could do that.
Just for the indexing, like to check the indexing with Z3.

##### **Chenyu** [[00:40:24](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2424)]
Yeah, I think that's a blocker for you.

##### **Sied Lykles** [[00:40:28](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2428)]
Yeah, I could do that.

##### **Geohot** [[00:40:34](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2434)]
I'll throw a $300 bounty on it.
Complete Z3 index validation behind a flag.

##### **Sied Lykles** [[00:40:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2445)]
Okay, yeah, cool.

##### **Geohot** [[00:40:48](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2448)]
It shouldn't be that hard, right?
I'm not thinking about something that should be.

##### **Sied Lykles** [[00:40:51](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2451)]
No, I think it should be pretty doable.

##### **Chenyu** [[00:40:57](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2457)]
Cool.
This might also fix the out of bounds, the current out of bounds bug.

##### **Geohot** [[00:41:07](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2467)]
Well, I think we want to leave the other one.
And I think this should be behind a flag because we don't really want to make Z3 a dependency of TinyGrad yet.
But I'm really excited about being able to validate mask stuff too.

##### **Chenyu** [[00:41:22](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2482)]
Yeah, I think the good part for Z3 is you can just incrementally add constraint.
So it's fairly easy for you to.
go through your AST.
And every time you see a valid, you can add that to the constraint.
And once you're done with that, you can pop it from your constraint set.

##### **Sied Lykles** [[00:41:43](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2503)]
Yeah.

##### **Chenyu** [[00:41:46](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2506)]
Yeah.
So fastdiv is pretty cool.
And it's basically rewriting the integer div into shift and mul.
So that's faster.
You say, in some case, we are better than NVCC?

##### **Sied Lykles** [[00:42:03](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2523)]
Um, yeah, I think cause for what I found, like then grad generally knows more about the upper bound, the number, like if you use a small loop variable and NVCC where you didn't make it, like it knows that it can make a use 16 and then it knows, then I remember emerging gone beyond the, like the upper bounded type that's using.
So in time, you actually know, okay, this is the longest balance.
This is the maximum of the loop variable.
This is the maximum this integer can be, and you can actually make the expression smaller.
Yeah, so the point is you multiply the number by a number and then you shift it, but the intermediate calculation can overflow, but
the lower, like the smaller, you know, your number is, um, sometimes you don't have to do the calculation in like int64, you can, you don't have to do the cast where it's more efficient, but I know I haven't seen it actually be faster when we were looking at the benchmarks.

##### **Chenyu** [[00:43:27](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2607)]
Yeah, I think.
You mentioned that with both fastdiv and fastmod, winograd is like 5% faster.
But those are also not behind us.

##### **Sied Lykles** [[00:43:38](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2618)]
Yeah.

##### **Chenyu** [[00:43:39](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2619)]
I think or some kernels is faster.

##### **Sied Lykles** [[00:43:44](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2624)]
Yeah.
Yeah.

##### **Chenyu** [[00:43:48](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2628)]
Great.
So good work on that.
Cool.
I think we are, as a whole, we want to move.
We want to try to use these three more.
And we will start with some of these tests, basically a more powerful fuzzer and making sure our rewrite rules are correct.
So this is the direction that we are excited about.
OK.
What's I said?
other bounty.

##### **Geohot** [[00:44:26](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2666)]
I changed the layout of the bounty spreadsheet a little bit.
I usually just kind of put the bounties in a random place.
I'm trying to keep the ones at the top being the most relevant bounties.
So it's going to be like, every time I add a new bounty, it pushes down.
You can see the Z3 index bounty.
For those that haven't seen, it's bounties.tinygrad.org.
The Z3 index is at the top.
Bounties that you can claim right now.
I think if somebody, does anyone here have a RDNA 4 card?
If you have an RDNA 4 card, easiest $150 of your life to add the tensor cores.
Like, literally, you're just going to have to, like, read the manual for 10 minutes, type the tensor core thing in from the manual, and it should work.
$300 if someone's got a 5090 out there to support that in the NV backend.
CPU graph working with Clang and LLVM if you don't have any hardware at all, $200 there.
And then those speed ones, those three speed ones about the matching engine speed, definitely accessible to anybody who knows Python pretty well.
And it's really important to us and that's why the bounty is large.
Are you going to move the div mod folding one?
I can move that one.

##### **Chenyu** [[00:46:02](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2762)]
No, I was just checking what that is because I don't remember.
Oh, yeah.
I think that was a different case.
B1TG, you want to talk about AMD LLVM compiler speed?

##### **B1TG** [[00:46:17](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2777)]
Yes.
Hi.
I was working on the AMD LLVM speed.
And now I got it faster than AMD backend with BERT layer equals 2.
But still 2 percentage slower with BERT layer equals to 24.

##### **Chenyu** [[00:46:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2805)]
I can test this, because our speed
This is like with default setting.
I don't know.
So do you know which kernels are faster and which are slower?

##### **B1TG** [[00:47:06](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2826)]
No.
I just run the test command from the CI.

##### **Chenyu** [[00:47:12](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2832)]
OK.
So if you are saying
We are faster with two layers, but we get slower with 24.
That means something in the layers are slower.
And if you are still working on this, I would suggest just use debug to print the kernels on the layers and see which one is slower.
I think each layer is.
There are three matmuls, and three matmuls with weight.
And your attention, that's your two big matmuls and some softmax.
Then you have an output of your attention.
And you have dropout.
So I think knowing which one is slower definitely helps.

##### **B1TG** [[00:48:05](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2885)]
OK.

##### **Geohot** [[00:48:07](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2887)]
I'll throw a $250 bounty on this.
AMD LLBM faster for BERT MLPerf and we use it for our submission.
So if you can actually make this faster and we end up using it for the submission, that bounty is yours.

##### **Chenyu** [[00:48:27](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2907)]
Yeah, so if you, I mean, I can test now, but I would much rather we first know if it's a single kernel that we are performing worse, or if it's a lot of stuff that we are generally worse.
Because for these, it seems like we want to at least match the flags.
And this noise is probably fine.
But if it's a very consistent diff, then we probably want to fix.

##### **Geohot** [[00:48:54](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2934)]
I'll say at least 5% faster.
Does that seem reasonable?

##### **Chenyu** [[00:49:03](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2943)]
I don't know.
Depends on how good you believe their compiler is.

##### **Geohot** [[00:49:12](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2952)]
5% plus faster for BERT MLPerf.
Because this should totally be doable.
It can't just be noise, right?

##### **Chenyu** [[00:49:23](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2963)]
There are other issues.
But now, if you put it as a...
If you put the bounty gate on the kernel speed, it's fine.
Because I also don't know if using the LLVM compiler is slower.

##### **Geohot** [[00:49:40](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2980)]
Oh, you mean to run it.
No, that's actually going to be faster.
That should definitely be faster.
You mean to do the beam search.

##### **Chenyu** [[00:49:46](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2986)]
I don't know.
Last time I tried, it was slower.
I can try it again.

##### **Geohot** [[00:49:51](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=2991)]
Oh, something's wrong if it's slower.
I mean, think about it.
Because when co-manager's doing it, co-manager has to run both basically Clang and LLVM.
How could this be slower?

##### **Chenyu** [[00:50:06](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3006)]
I don't know if you want to put that as part of the bounty.
I was just saying I tried it last time.
It wasn't slower.

##### **Geohot** [[00:50:13](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3013)]
Oh, well, the part of the bounty is that we use it for our submission.
So if we use it for, I don't really care if it's slower, if it ends up being slower.
5% faster kernel time.
And then not unusably slow, but if it's a little bit slower, who cares?

##### **Chenyu** [[00:50:27](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3027)]
I care.
What?
We have 13 minutes.

##### **Geohot** [[00:50:32](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3032)]
Oh, it's a little bit slower.
But if the kernels are 5% faster, what are you searching for anyway?

##### **Chenyu** [[00:50:35](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3035)]
I mean, you know that now that if we search for two hours, it's also 5% faster, huh?

##### **Geohot** [[00:50:43](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3043)]
Well, yeah.
So that's what I mean.
We've got to use it for our submission.
But it's not going to be too much slower.
I don't know.
LLVM is great.

##### **Chenyu** [[00:50:50](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3050)]
OK, B1DG, I hope we don't confuse you.
But the goal is to figure out which kernel is slower, see if it's a flag that we are missing or something.
And basically, the bounty is yours once you figure out that and fix that.
As long as the compile time is similar and the speed is faster, we definitely will use that for our submission.
And if it's gated on submission, you have about two weeks to do that.
Because after that, we need to make our submission run.

##### **Chenyu** [[00:51:25](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3085)]
So that's the criteria.
And if you have anything that you want me to try, just let me know, and I will try it.
OK.
Let's see.

##### **Geohot** [[00:52:09](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3129)]
Llama 4 Scout.
If someone has previously claimed a bounty and you would like access to a tiny box red, let me know.
And then, yeah, you can download Llama 4 Scout on the tiny box red.
And you should be able to load it in and get it running faster than 200 tokens per second.
You got yourself $500.
So 200 tokens per second is not that crazy.

##### **Chenyu** [[00:52:40](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3160)]
What's the limit?

##### **Geohot** [[00:52:45](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3165)]
Like 400?

##### **Chenyu** [[00:52:48](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3168)]
I see.
So also 50%.

##### **Geohot** [[00:52:51](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3171)]
You know what?
I'm going to relax it.
I'll relax it to 100 tokens per second, because you've got to go across the GPUs.
What's our LLAMA?
What's our llama speed across the GPUs?

##### **Chenyu** [[00:53:13](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3193)]
You mean one llama split into four?

##### **Geohot** [[00:53:17](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3197)]
Yeah, yeah, yeah, because it's basically the same thing.
Yeah, we can just do split on the Llama.
I think it's not that good.

##### **Chenyu** [[00:53:40](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3220)]
Yeah, so it's 18.66 milliseconds for one and 14 for four.

##### **Geohot** [[00:53:50](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3230)]
Yeah, yeah.
I mean, the Llama 4 Scout is basically the same access as 7B.

##### **Chenyu** [[00:54:01](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3241)]
If you do Llama 4 Scout with FP8.
fp8 uh yeah they didn't really merge fp8 

##### **Geohot** [[00:54:20](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3260)]
oh no no no no no no okay never mind this bounty is not claimable nobody can claim this is impossible scout doesn't even have fp8 really like they didn't release an fp8 one
Should we merge FP8?
I don't know.
It just looked like a lot of crap.
I don't know if it was badly done, or it just looked like a lot of stuff in that PR.
I think we got to merge it.
Yeah.
He's here.
I think we got to merge it.

##### **Geohot** [[00:55:03](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3303)]
Want to test it?
I can test it.
I don't know.
Want to test it?
Test how fast it is?

##### **Geohot** [[00:55:12](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3312)]
Oh, I don't care how fast it is.
Let's just test it for correctness.
Are the tests good to test for correctness?

##### **Chenyu** [[00:55:19](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3319)]
Oh, OK.
I will review it tomorrow.
Cool.

##### **Geohot** [[00:55:22](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3322)]
Sounds good.
Yeah, we got to get that merge.
We can't just let that sit there.

##### **Chenyu** [[00:55:27](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3327)]
Otherwise, you will have forcing.
Yeah.
OK.
I will review it tomorrow.

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3336)]
Great.
And I will lock this bounty right now.
and move it to the top.
It's a high priority.
Actually, what's more exciting about FP8 is... 

##### **Chenyu** [[00:55:55](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3355)]
We're going to use that for MLPerf.

##### **Geohot** [[00:55:54](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3354)]
Yeah, we're going to use it for BERT.

##### **Chenyu** [[00:56:02](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3362)]
I don't know.
Maybe that can wait for the next cycle.

##### **Geohot** [[00:56:06](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3366)]
Oh, not this cycle.
Yeah, but next cycle.
OK.
I'm locking this FP8 bounty, and we will review it tomorrow.
OK.
Cool.
Sounds good.

##### **Chenyu** [[00:56:29](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3389)]
OK.
I don't know what to comment on all the attempt on test failure 53 and similar stuff.

##### **Geohot** [[00:56:40](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3400)]
The failure 53 one I don't like.
That doesn't even... The other one has like an explanation, and I have to sit down and see if I understand it.
I'm going to work on the linearizer tomorrow.
I have a fix for the other bug in the linearizer.
There's another bug in the linearizer where if it creates a block fork and it creates a block before it, if it needed a block end, it doesn't insert one.
So, yeah.
Yeah, so I will look at the 53 one.
I want an understanding of what's wrong.
It just looks like a change that happens to maybe randomly fix it.
But the one that fixes the average pool failure seems better.
So I'll block that bounty, and I'll review it tomorrow.

##### **Chenyu** [[00:57:18](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3438)]
OK.
Sounds good.
And with that, I think that concludes this meeting.
Thank you, everyone, and see you next week.

##### **Geohot** [[00:57:38](https://www.youtube.com/watch?v=BQQqrUqe1VA&t=3458)]
Bye.

