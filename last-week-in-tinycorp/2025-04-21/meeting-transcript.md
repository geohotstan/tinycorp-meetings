# 2025-04-21 Meeting

### Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time)
- company update
- new linearizer
- bert, mlperf, hcopt
- scheduler kernalize
- driver
- webgpu
- retinanet
- onnx
- cloud scale uuuvn stuff
- locals
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=-ayeO_SKx70)

### Highlights

- **[NOTE TO TINYGRAD CONTRIBUTORS](#chenyu-004658)**: "empathize with reviewers" or just split PRs up so they're individually easy to click merge

- **[Company Update](#geohot-000006)**: 100 RTX 5090s arriving; TinyBox Green 2 will honor original price for those with wire transfers; a 15% price hike ("Liberation Day tax") expected for late orders.

- **[New Linearizer](#geohot-000107)**: Vastly improved; eliminates while-loop and now supports O(1) graph rewrites; focus shifting to micro-benchmarking UOP creation and toposort performance.

- **[Multi-scheduling Improvements](#geohot-000216)**: Plan to rewrite multi-scheduling to be O(1); aim to support Tenstorrent-style 2D sharding with each core acting like a small GPU.

- **[Scheduler Kernelize](#qazalin-000746)**: Kernel graph now captured in tensor UOps; simplifies JIT and avoids triple AST captures; backprop handling still needs work.

- **[JIT Refactor Plan](#geohot-000711)**: Remove redundant classes and streamline kernel capture logic post-kernelize.

- **[BERT + MLPerf](#chenyu-001320)**: Fused `arange` for embedding saves ~7ms; instability with AM driver, fallback to AMD driver; goal to submit candidate runs within 10 days.

- **[RetinaNet](#flata-001837)**: Post-processing and BEAM logic in focus; issues with AM driver cause NaNs; AMD setup more stable; optimization focus is post-processing speed and logging.

- **[Driver Issues](#nimlgen-002206)**: Firmware stability varies across machines; current best bet is Tiny13 with updated firmware; plan to fetch firmware from web to avoid machine dependency.

- **[WebGPU + Model State](#hooved-002829)**: Proposed PR captures model state (RNG, KV cache) by tracking realized tensors across JIT calls; Geohot recommends basing persistence on actual reads/writes, not buffer presence.

- **[ONNX Fuse Concerns](#chenyu-003811)**: Fusing sometimes leads to redundant ops and slower performance; plan to isolate and test patterns like `fuse arange`.

- **[Cloud & UUVN](#uuvn-004132)**: InfiniBand gradient averaging works with 3 GPUs per machine but not reliably with 6 total; PRs need to be split into single-purpose changes for mergeability.

- **[FP8 + Metal + PTX Issues](#chenyu-004938)**: FP8 support in Python backend questioned for missing NaN support; PTX broke after linearizer refactor—need a test for future tracking.

- **[Z3 & Bounds Checking](#chenyu-005212)**: Positive feedback on Z3 integration; some grouper rules need review; direction looks good.

- **[Tenstorrent Bounty](#geohot-005310)**: Lock criteria: all ops tests must pass and support multi-core scaling; model tests not required; performance can be improved later.


### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=-ayeO_SKx70&t=0)]
Let's get started. Any company update?

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=-ayeO_SKx70&t=6)]
so I've been sick all week I got sick Wednesday I'm still not feeling great. All we really got company update wise is we do have 100 5090s coming we seriously overpaid for them so yeah but you know I don't really see it getting better anytime soon
So we do have 100 5090s coming.
We are going to honor the price of the TinyBox Green 2 for those who managed to get a wire in.
And for those who didn't get a wire in, I think we're going to do like a 15% price hike.
We'll call it the Liberation Day tax.
But I got to set that up.

##### **Chenyu** [[00:00:49](https://www.youtube.com/watch?v=-ayeO_SKx70&t=49)]
Okay, sounds good.
Cool.
I mean, feel free to say no, but do you have anything to say for the new linearizer?

##### **Geohot** [[00:01:07](https://www.youtube.com/watch?v=-ayeO_SKx70&t=67)]
It's a lot better.
It's good.
The main thing I'm happy that it removes is the old linearizer had, oh, we can also remove the block fork UOp.
It's not used anymore.
The old linearizer had a while loop.
and would have to do O(n) graph rewrites.
O(log(n)) graph rewrites.
But the new one is just O(1) graph rewrites.
So that's pretty nice.
It's a bit faster.
And none of the slowness is in the linearizer itself.
The thing I'm going to work on this week is...
I'm going to write a whole set of micro benchmarks for things like UOP creation and tuplize and toposort and like the UOP children stuff.
I think if I could get speed up there, that's like the biggest place that all the time is being spent now.
But yeah, overall, I'm pretty happy with the Python speed.

##### **Chenyu** [[00:02:10](https://www.youtube.com/watch?v=-ayeO_SKx70&t=130)]
You're also interested in the multi-scheduling speed?

##### **Geohot** [[00:02:16](https://www.youtube.com/watch?v=-ayeO_SKx70&t=136)]
Yeah, so that one, the multi-speed is mostly going to just be rewriting multi.
And that's... Well, so...
It's not really Python, no.
I mean, Python speed should translate to multispeed, but only in a linear way.
But the real thing for multi is just to go from O(n) to O(1).
I have a small thing write up about it.
But really, what I want to do is think about how to support Tenstorrent with new multi.
Because if you can support Tenstorrent, you can really support everything.

##### **Chenyu** [[00:02:56](https://www.youtube.com/watch?v=-ayeO_SKx70&t=176)]
We want each core kind of to be one small GPU.

##### **Geohot** [[00:03:01](https://www.youtube.com/watch?v=-ayeO_SKx70&t=181)]
Yeah, that's the basic idea.
Each core is a GPU, and then you shard things in a two-dimensional way.
So you can shard a matrix across the whole thing two-dimensionally.
Because I'm starting to think that things are going to look more and more like the Tenstorrent hardware.
In the sense of, actually, I was reading the Blackwell has a whole new kind of tensor core, B200.
And this new kind of tensor core, a few things.
I didn't realize all tensor cores are basically systolic arrays, as far as I can tell.
Like that's actually how they're implemented.
I didn't know this.
I didn't know that like the TPU actually just exposes the fact that it's a systolic array, but they all are systolic arrays.
So yeah, I've been having nice conversations with O3 about GPU microarchitecture.
But yeah, so the B200 is basically a big systolic array.
I think it's 128 by 128.
So they're looking more and more like the TPU.

##### **Chenyu** [[00:04:16](https://www.youtube.com/watch?v=-ayeO_SKx70&t=256)]
What's fundamentally different between 1D sharding versus 2D sharding?

##### **Geohot** [[00:04:24](https://www.youtube.com/watch?v=-ayeO_SKx70&t=264)]
Nothing fundamental.
It's just you shard in two axes, right?

##### **Chenyu** [[00:04:25](https://www.youtube.com/watch?v=-ayeO_SKx70&t=265)]
Yeah, but you can imagine that it's similar to you flatten that and just shard 1D.

##### **Geohot** [[00:04:38](https://www.youtube.com/watch?v=-ayeO_SKx70&t=278)]
You flatten it and shard 1D.
Is that the same thing?
Well, what do you mean by you flatten it?
No, that's not the same thing.
You can't do that.

##### **Chenyu** [[00:04:47](https://www.youtube.com/watch?v=-ayeO_SKx70&t=287)]
So do you want to support shard one way with copy and shard another way with real shard?
Because if we do copy, if it's copy, copy, then it's the same as single copy, right?
And if it's like real shard, real shard, then it's kind of similar to you do a real shard on your flatten.
The only different case, I think, is you copy shard one way and real shard another.

##### **Geohot** [[00:05:22](https://www.youtube.com/watch?v=-ayeO_SKx70&t=322)]
uh so I don't really see how it's the same thing right like think about just a matrix and you're trying to shard it on four gpus right so i have a 2d matrix and i'm trying to shard it on four gpus so if i shard it on one axis i'm gonna get like four vertical lines but if i shard it on two axis i'm gonna get four squares
Yeah, but I don't think there's a way to like mimic that.
I mean, you're sure you could do like fancy, you could do like fancy reshapes.
Oh, yeah.
And that's, I think, fundamentally what it will be.
I think we can we can totally do that.
And like, that's just a question of how to express it.
But fundamentally, it's just the shape tracker, right?
And like, you want to kind of keep the view as expanded as possible.
But

##### **Chenyu** [[00:06:11](https://www.youtube.com/watch?v=-ayeO_SKx70&t=371)]
I think for 2D and maybe more sharding, we might need to start to think about your connection between shards are not identical for all flows.
Now we assume your P2P is the same.

##### **Geohot** [[00:06:34](https://www.youtube.com/watch?v=-ayeO_SKx70&t=394)]
I mean, Tenstorrent shouldn't have to deal with that problem.
yeah sure eventually we'll get to like like uh heterogeneous like like yeah but that generally i think usually can be expressed yeah sure and then you're doing like something like max flow uh yeah you should definitely be able to well the new multi is gonna have like an all reduce uop and then the all reduce uop we could have a separate thing which does the scheduling of that communication

##### **Chenyu** [[00:07:08](https://www.youtube.com/watch?v=-ayeO_SKx70&t=428)]
That sounds good.

##### **Geohot** [[00:07:11](https://www.youtube.com/watch?v=-ayeO_SKx70&t=431)]
But no, I still have... I'm still going to work this week on... Well, the other big thing that I want to do now that kernelize is merged is I want to do the... I want to refactor the JIT.
I want to refactor the JIT to not have all those stupid classes anymore and just basically capture a kernelized thing.

##### **Chenyu** [[00:07:33](https://www.youtube.com/watch?v=-ayeO_SKx70&t=453)]
Sounds good.
We can talk about scheduler kernelize since we talked about it.

##### **Qazalin** [[00:07:46](https://www.youtube.com/watch?v=-ayeO_SKx70&t=466)]
docs.tinygrad.org
There's kernelize section.
You can read it.
The idea, basically, is that we can have kernels inside the Tensor.
So what this allows us to do is to build incrementally
the schedule graph and then actually make the execitems out of it so that that's going to like make the JIT much more simpler because right now the JIT is doing in capturing of the AST it's
doing three runs.
It's running once to capture the ASTs, it's running the second time, and then it's running the third time.
So this is going to remove all that because the kernelize, the entire graph of kernels is captured in the tensor uops itself.
So that is merged.
I have a diff for backward.
I don't know if it's correct.
If you can take a look at that one.
And yeah.
9953.
So it doesn't work with gradients because I want gradient to sort of treat the kernelize as a buffer.
So that's the only thing that's left.

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=-ayeO_SKx70&t=553)]
So yeah, I see you saying here that
You're treating assign like detach and saying it doesn't have a gradient.
I don't necessarily think that's right.
I mean, I don't know about how this interacts with backwards, but you should definitely be able to take the gradient of things that were assigned to, and it should work as you expect.
Like, think about doing, like, ReLU in place.
I mean, in TinyGrad this stuff's a little bit different because it's not, like, really an assign.
Like, assign doesn't always mean that it's going to be assigned.
But I don't think treating it like detach is right.
Like, if you think about, like, a normal, like, uh...
gradient flow, if I have assigns, why should that affect anything?

##### **Qazalin** [[00:10:33](https://www.youtube.com/watch?v=-ayeO_SKx70&t=633)]
I think it should just ignore it.

##### **Geohot** [[00:10:40](https://www.youtube.com/watch?v=-ayeO_SKx70&t=640)]
But that's not what this does.
It doesn't ignore it, it treats it the same as detach.
So what you're saying here is that gradients can't flow through assign.
Which I don't think is right, but it's okay.
I think this is probably more correct than what's in there.

##### **Qazalin** [[00:11:11](https://www.youtube.com/watch?v=-ayeO_SKx70&t=671)]
Apparently it asserts because it tries to actually get the gradients of an assign.
The assign from the perspective of the child tensor is a buffer.
Is a load.

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=-ayeO_SKx70&t=682)]
well but not always right? 

##### **Qazalin** [[00:11:25](https://www.youtube.com/watch?v=-ayeO_SKx70&t=685)]
always always in this case always 

##### **Geohot** [[00:11:28](https://www.youtube.com/watch?v=-ayeO_SKx70&t=688)]
no no no come on what if I oh oh because the assign uop isn't created if i don't have a buffer it'll do a replace uop 

##### **Qazalin** [[00:11:42](https://www.youtube.com/watch?v=-ayeO_SKx70&t=702)]
uh well if you have a source as an assign
The thing that goes into the local kernel for that child is the buffer, not the assign.
It doesn't mean anything to have an assign in the middle of the kernel, right?
Assign is a memory boundary, just like how buffer or copy is a memory boundary.

##### **Geohot** [[00:12:04](https://www.youtube.com/watch?v=-ayeO_SKx70&t=724)]
Yeah, but only tensor.py is enforcing this, right?

##### **Qazalin** [[00:12:08](https://www.youtube.com/watch?v=-ayeO_SKx70&t=728)]
Yeah 

##### **Geohot** [[00:12:12](https://www.youtube.com/watch?v=-ayeO_SKx70&t=732)]
I think it's fine for now, but I think that we should probably change the story around tensor.
I think, like, we should always put the assign in the uop graph and then remove assigns that don't make any sense later on.
Like, we shouldn't be using if statements in tensor to gate that.
I think it can have it later.
Yeah, no, good work getting it kernelized merged.
I'll look over the docs, and I'll check it out, make sure it's right tonight.

##### **Chenyu** [[00:12:45](https://www.youtube.com/watch?v=-ayeO_SKx70&t=765)]
Yeah, I just read.
I was reading the doc.
It looks fine.
Do we add this to CI as well, to making sure the code is runnable?

##### **Qazalin** [[00:13:00](https://www.youtube.com/watch?v=-ayeO_SKx70&t=780)]
Well, I think the test docs already checks that, yeah.

##### **Qazalin** [[00:13:04](https://www.youtube.com/watch?v=-ayeO_SKx70&t=784)]
So we check everything in the doc, I see.
Yeah, I think.

##### **Geohot** [[00:13:12](https://www.youtube.com/watch?v=-ayeO_SKx70&t=792)]
Yeah, there's no asserts, but it actually runs in the doc.

##### **Chenyu** [[00:13:20](https://www.youtube.com/watch?v=-ayeO_SKx70&t=800)]
OK.
Yeah, looks fine to me.
I think for people in this call, if you're interested, go to docs.tinygrad.org
docs.tinygrid.org/developer/kernelize
Read it, see if you can understand it.
If not, feel free to post your feedback or if you have any suggestions to the docs channel.
And with that said, okay, let's go back to BERT.
What did I do?
I put in a hack to fuse Arange, but only fuse it for embedding.
I don't know how to not do that.
So for now, the hack is just saying if it's uint.
There's another flag called fuse Arange uint, and you can disable uint so that you won't fuse RAND.
And with that, I think that saves like seven milliseconds for everyone.
And for some reason, it doesn't really work for the MI300x ones.
I don't understand.
Anyway, I plan to do some submission candidate runs this week.
We are fairly close to a deadline.
It's like 10 days.
I will prepare those, see where we are.
Try to get the single kernel softmax in.
It adds a lot of total compute that I don't quite understand.
I would probably look slightly more, but we will talk of this in the retinanet.
I will try to see if there's anything I can help this week for retinanet.
We want to get something in for retinanet.
So I'll probably do more of that instead of tuning BERT more this week.
I will leave the BERT red run to Nimlgen if he can find anything to fix the AM driver.
Otherwise, I will just do what I'm doing now, which is running the BEAM with AM and running the real run with AMD.
That's the only stable setup I can find to run this.
And finally, for hand coded optimization, I made a few changes.
I removed require optimization.
because by removing that, our gated load statements and some kernel change slightly, but the benchmark compile3.py become faster.
So the benefit of complexity and no one really knows what that does.
I just remove it.
And with the removal of that, I can make hand code optimization to just return a list of OPTS.
OPTS are the actions that we apply on the kernel.
It was annoying because required optimizations, you call it sometimes, and it adds actions sometimes.
Now, hand coded optimization just return a list of op.
And my next project after we wrap up MLPerf would be trying to find a better full pass or a better hand coded optimization.
And that API is better because now we separate the creation of a kernel to finding what
Actions are good to apply for the kernel.

##### **Geohot** [[00:17:04](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1024)]
Yeah, I really like the separation.
And I think that those optimizations can start to go in the kernel graph.
So yeah, we could put it in the graph such that it's not this out of band thing anymore.
Because I find it pretty annoying when I'm working inside a tensor if I want to change the optimizations on something.

##### **Chenyu** [[00:17:29](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1049)]
You need to print the AST then do... 

##### **Geohot** [[00:17:35](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1055)]
I mean, I can schedule it and then hand create the kernel object and then optimize it.
So I think we should add a pass in between kernelize and schedule called kernel optimize.
And kernel optimize will add to each kernel in the tensor graph the optimizations.
And it'll either get them from a hand-coded policy or from a beam policy.

##### **Chenyu** [[00:17:59](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1079)]
I see, OK.

##### **Geohot** [[00:18:02](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1082)]
Yeah, so I would do it like that.
And then we can totally separate that from the schedule.
Yeah, it's like in the graph, optimizations, connect to kernel.

##### **Chenyu** [[00:18:21](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1101)]
OK.
That's my stuff.
I mean, Flata if you want to speak, if you can speak now, you can speak now.

##### **Flata** [[00:18:37](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1117)]
or hi oh hey uh yeah so for retinanet i think uh for the most part i've just been uh i actually started working on the post processing and um i kind of spent some time on the beam stuff so but i'm switching gears onto that but i think the beaming uh
The AMD driver, there's still some hanging issues.
I extended the flag that Chenyu suggested to be larger, but that didn't end up working, so it's still hanging.
For the AMD driver, I thought initially I was successful with both non-beam and beam benchmark runs, but at some point there will be a case where the loss is just NAN, and it's pretty difficult to reproduce on my end.
So I guess I know, Chenyu, you mentioned about helping out on the retinanet.
So maybe if you can help me out on that, and if there's anything you want me to add, like flags or anything like that, to help you assist with debugging it further, I can definitely do that.

##### **Chenyu** [[00:19:34](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1174)]
Yeah, OK.
So I think we kind of only have this week, and we kind of want to submit something.
So I think the priority would be have a setup
whatever using AMD or AM driver, we probably need to still do BEAM, but we want something that can run on a red machine.
So that's a priority.
And I think, I don't know, maybe Nimlgen can help with the AM issue, but I think I will try this, like the BEAM with AM so that it doesn't hand and run with AMD thing, similar to how I'm doing BERT later.
So I think that's one priority.
Then another is we need to find a way to speed out the post-processing.
I think that's the most important one, because that dictates how many runs we can do.
We need, I think, five?

##### **Flata** [[00:20:30](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1230)]
Yeah.
Also, I was going to say the non-beam runs for both AM and AMD, if I remember correctly, they are stable.
So obviously not going to be as fast as we wanted it to be, but we at least know the baseline of the non-beam runs are fine.

##### **Chenyu** [[00:20:51](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1251)]
Yeah, I mean, even if I said whatever time, we still want to give a representable, good enough time.
So I think what you can do is I'll check post-processing, but you probably know more than me at this point.
See what error can be run on device instead of NumPy and stuff.
And also, we need to start preparing the logging.
I have a comment on your init mlperf thing.
But other than that, we also need to do some logging, because you only know the logging are correct after you have a full run.
And we need logging to be correct.
That's also important for us to make a run.
But otherwise, looks good.
We can continue syncing on this in the
the retina net channel.

##### **Flata** [[00:21:53](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1313)]
OK, sounds good.
Thank you.

##### **Chenyu** [[00:21:58](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1318)]
With that said, let's move on to driver.

##### **Nimlgen** [[00:22:06](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1326)]
Yeah, so for the BERT run,
So I'm testing this right now on three machines.
So for Tiny11, I haven't seen any NANs, but it's, it has another problem with file system, I guess.
So just, yeah.
So it gets your error from time to time.
So, but yeah, but actually it wasn't the latest firmware.
So for now I just updated to Tiny13.
I'm just still testing this, like, to the latest 6.4.
So yeah, I'm just testing.
So far so good, but yeah, it's only two runs.
So yeah, I'll test it on the latest firmware.
We'll see.
So yeah, because our fleet, like, uses pretty old 6.1.3 firmware, so yeah.
Maybe there's something wrong with this.

##### **Chenyu** [[00:23:13](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1393)]
So you can reproduce it, and you think its the version?
If I want to do a run now, what would you advise me to do?
I pick a machine.
How do I...
Maybe you can post that in BERT Channel or somewhere for instructions for me to making sure I'm using the correct or your advice version.

##### **Nimlgen** [[00:23:39](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1419)]
Yeah, okay, I'll check that.
So if Tiny13 is fine on this version, yeah, I'll post it.

##### **Geohot** [[00:23:48](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1428)]
Yeah, I really like the idea of grabbing the firmware from the web instead of relying on whatever happens to be on the machine.
Like, we should need nothing on the machine at all to run with the stuff.
And then we can fetch always the same firmware version, so this is just never a machine-specific thing.

##### **Nimlgen** [[00:24:05](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1445)]
Mm-hmm.
Okay.

##### **Geohot** [[00:24:10](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1450)]
um how big is all the firmware?

##### **Nimlgen** [[00:24:16](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1456)]
oh uh i know it's like 10 megabytes maybe 

##### **Geohot** [[00:24:20](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1460)]
yeah we should always be downloading that from the web. It shouldn't even be accessing it from the one that's on disc 

##### **Nimlgen** [[00:24:30](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1470)]
um yeah so that's for BERT so for the speed i also tested that and um so i looked into that so there is pretty strange
problem is that, so running some kernels, so like the second run or just like second, third, and so on runs, so they're just slower than the first run when it's running with AM.
I tested the AMD GPU driver with their power management and with their stuff, but with MES disabled, so in their driver.
So they have the same problem.
But if MES is enabled, so they can also have pretty decent timing.
So I'm not sure why that happens.
They are so still.
And I will take a look into that.
So yeah.

##### **Chenyu** [[00:25:26](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1526)]
OK.
I think it's only like 2%, 3% in terms of our run since
This is more of a benchmark for us.
I would prefer to use AM through.
Then in the next round, we compare with our current round.
So I would run whatever you recommend me to run with.
And as long as it doesn't have NAN issue, I think 2%, 3% of it is fine.
And it is not a top priority now to figure out why
if that's the issue, unless you have a very easy fix.
I think it's not that important now for this run.
But we definitely want to fix that longer.

##### **Nimlgen** [[00:26:13](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1573)]
Yeah, so for, yeah, OK, I'll post it once, tiny13.
OK, I'll just test in tiny13 and post it if it's good.
So for the USB GPU, so yeah, actually, we're going
patch the firmware for the 24 version.
So yeah, writes are working.
So I started to move in some abstractions into master.
So yeah.
Yeah, so the current plan, I'll
merge all the abstraction we needed into master maybe i still think that i'm pretty close to the rethink to make it work because um actually like the whole usb control logic is pretty simple it just has like one function to get to handle on all interrupts
And they have one big while loop.
And I think in this while loop, they should just pull somewhere inside this while loop, they should pull the NVMe.
So yeah.

##### **Geohot** [[00:27:32](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1652)]
Yeah, we should make a repo with all our reverse engineering efforts on the firmware and just whatever changes we have and all that.

##### **Nimlgen** [[00:27:42](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1662)]
Yeah.
Yeah, maybe I have one.
I just post something from time to time into, yeah, maybe it's not the decent quality, but yeah.
Okay.
Um, so yeah, it's, it's, it's working.
So the plan is just to get everything like, like to get all the abstraction merged.
And yeah, after that, I'll just revisit the read speed.

##### **Chenyu** [[00:28:19](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1699)]
That's good.
Okay, let's move on to WebGPU.
I guess for hooved the memory planning, whatever.

##### **Hooved** [[00:28:29](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1709)]
Yeah, I can comment on that.
First, I just mentioned, of course, the planned refactoring of the JIT will be relevant for WebGPU, so I'm interested in that.
Yeah, so most of the stuff are not, I mean, the memory planning in the JIT thing, like the memory planning part
of that PR actually probably isn't that important.
I haven't tried really, but I haven't seen a real memory savings on a real model that's actually large.
But the actual motivation and the important part of that PR is the part around model state.
I think I've found what I would say is the most pure definition of, or the most pure way to define model state so far.
It captures RNG counter, RNG buffers as well as KV cache.
Basically, let me explain it this way, why it's meaningful.
So when tensor.realize finishes executing, all the buffers that are allocated during tensor.realize and the execitems, they get garbage collected.
Assuming you're not capturing with the JIT, they get garbage collected, except for, of course, the ones that are still attached to uops, which are attached to tensors, which are
the ones that were real, the tensors that were realized, as well as all the other tensors alive in the program that were affected by becomes map.
So, you know, just the way that Tinygrad is set up right now, like those buffers that still are alive,
Those are the ones that need to persist between calls to the JIT, at least as far as I can tell.
So the important part of that PR is just
that I capture those on the second call to the JIT.
The buffers that are realized after the first call are marked on the second call to the JIT.
And that's the necessary and sufficient set of buffers that are needed to take your model from where it was in TinyGrad and then pick it up where you left off elsewhere in another context.

##### **Geohot** [[00:31:06](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1866)]
Yeah, I mean, I just, I don't think that that's right.
I think that, like, this is based on the assumption that buffers containing data that must persist after the first call to the JIT.
Like, again, I think that that buffer could be allocated, that buffer could be not allocated.
Whether it matters for the JIT, you can tell from the computation that JIT is doing.
If you have a buffer there that happens to be allocated that then is getting completely overwritten by the third kernel in the JIT and is never read from, there's no reason that buffer should be in your set.

##### **Hooved** [[00:31:43](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1903)]
You're right about that in terms of it being completely overwritten and never read from again.
So the example I pointed out, the KV caches, those are not completely overwritten and they're read from again, but they're not captured by our previous definition of model state.

##### **Geohot** [[00:32:05](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1925)]
Well, then it might be wrong.
That definition might be wrong.
And I don't know if we're distinguishing overwritten completely versus not overwritten at all, but we definitely know that from the compute.
My problem with this way of doing it is it depends on really state that's completely arbitrary, when all of this state can be determined from what the computation is itself.
You shouldn't be asking the question what...
Yeah, you shouldn't be asking the question, what buffers are allocated?
You should be asking the question, what bytes are being read from that are not written to by me, or being read to before they're written to by me?

##### **Hooved** [[00:32:55](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1975)]
Yeah, we would have to go beyond just looking at the buffers.
We'd have to look at the bytes.
I think I agree with that.

##### **Geohot** [[00:33:05](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1985)]
Yeah.
You can look at just the shape tracker and the output will tell you if something's going to be completely overwritten or not.
If it's a mask store, it won't be.
But that's like one line check.
It's not a...

##### **Hooved** [[00:33:17](https://www.youtube.com/watch?v=-ayeO_SKx70&t=1997)]
Yeah, I'll look at that.
Thank you.
But yeah, so the refactor of the JIT, that could change together with the kernelized stuff.
It's very interesting for this.

##### **Geohot** [[00:33:37](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2017)]
If you want to start playing with that, go ahead.
Similar to the prevent Viz from blocking the GC of buffers PR, I commented on this.
PRs like this are never going to be merged.
A PR that explicitly adds 30 lines of code to work around something that's fundamentally wrong.
When I see a function...
you have a function called something like yeah restore original buff uops that just shows something's wrong right that's that's like i would never merge something like that um because it's not yes i understand it may fix the problem but it's not about fixing today's problem it's about building the right thing for for five years from now 

##### **Hooved** [[00:34:26](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2066)]
i agree with that philosophy

##### **Geohot** [[00:33:30](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2010)]
Cool.
I'm going to spend this week on micro benchmarks.
Do you see what I mean by the new way to write the JIT with kernelize?

##### **Hooved** [[00:34:44](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2084)]
I understand the kernel graph.
I think I do, but I can't articulate it in a couple sentences.

##### **Geohot** [[00:34:54](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2094)]
Well, then you're welcome to play with a PR that just inherently by design fixes these things.
You don't want to fix bugs.
You want to design such that the bug is impossible.

##### **Hooved** [[00:35:08](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2108)]
I agree.
And so just if we're talking about the Viz stuff,
It's just based on wanting to keep UOPs around, but having the problem that the buffers can't go away if the UOPs are around.
So we would have to fix that.
Sorry, did you say that made sense?

##### **Geohot** [[00:35:33](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2133)]
I said, yeah, sounds good.
OK, we have to fix that.
Cool.

##### **Hooved** [[00:35:48](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2148)]
Yeah.
If anyone sees an easy fix for that, I'm happy to give up any share of the bounty.
But yeah, I am interested.
And I can't promise that I'll deliver something soon for that.
But yeah, I agree.
That would be the ideal solution.

##### **Geohot** [[00:36:04](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2164)]
Yeah, no, but I mean, that's the whole, like, that's the work, figuring out how to do it, right?
Like, I don't see a quick fix, but I mean, the first step kind of is to just figure out even what we are doing right now.
I guess, I don't really know.
Like, what is the relationship?

##### **Chenyu** [[00:36:18](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2178)]
For a suggestion to move this specific topic around, I think it would be useful if you just open an issue and kind of describe
you just said into the issue like write it down and also describe what we are doing now and what we expected to be um or to be fixed because for now even you even if you even if you say okay uh someone maybe if you are interested can look into this for now for for me i don't
really understand what needs to be looked into, let alone other people who might be interested in solving this.
So I think documenting.

##### **Hooved** [[00:37:02](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2222)]
Was the PR not clear?
Because I thought I outlined it, but maybe it's too verbose.

##### **Chenyu** [[00:37:11](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2231)]
PR is a collection of code change as in commit.
It's not that effective to really.
You know this because you went through all the PR changes and iteration.

##### **Hooved** [[00:37:24](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2244)]
Yeah, OK.
Yeah, I can open an issue.

##### **Chenyu** [[00:37:24](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2244)]
I think having an issue would be nice.

##### **Hooved** [[00:37:28](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2248)]
Definitely.
Thank you.

##### **Chenyu** [[00:37:35](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2255)]
OK.
What's next?
So we have done RetinaNet.
For ONNX.
I will review the Hugging Face CI thing later.
comment on that fuse, because I also find it sometimes work, and sometimes it doesn't work.
And I'm not entirely sure why.

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2284)]
Do you have a bug?
Do you have a test that's failed?

##### **Chenyu** [[00:38:11](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2291)]
Yeah, I can write.
It's not about tests that fail.
It's like every time I add fuse, it becomes slower.

##### **Geohot** [[00:38:21](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2301)]
All I can do here is I can describe the behavior of fuse.

##### **Chenyu** [[00:38:27](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2307)]
What I can do is I can give an example and say fuse versus no fuse and why it double ops or something.

##### **Geohot** [[00:38:38](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2318)]
I could look into those.
What I'm really interested in is fuse versus no fuse, like fuse is wrong.
And there's definitely things that don't linearize, but things that don't linearize are different from things that are wrong.
It should never be wrong.

##### **Chenyu** [[00:38:54](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2334)]
Yeah, I think it's correct.
I think it's correct.
It's just for some reason it's doing duplicate the computer or something.

##### **Geohot** [[00:39:08](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2348)]
If you write a test for it that just has the two ways and says this one's doing double the flops or something, and I can look, it should be an easy automated test to write.
Just look at global counters, global ops.

##### **Chenyu** [[00:39:18](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2358)]
Yeah, sure.
Yeah, I pose it in BERT for the single kernel softmax, but I imagine that's too big of a test.
I can find something that's similar.
And specifically for sort,
I understand sort use a lot of that, and making cat faster is a thing.
So let's add the Fuse Arange thing to the example.
And maybe even better if we can add this as a maybe find a smaller version of this and add it as a test, Arange test.
what file would be suitable for this.
Basically, we want to understand the behavior, what part it saves, what kind of UOP it's saving and stuff.
So that it's not only on this example, but it's on this pattern, and we have a way to maintain this pattern moving forward.
At some point, we will make fuse Arange behavior, like a default.
And at that point, having all these examples and tests would help.

##### **Geohot** [[00:40:45](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2445)]
OK.
That's good.

##### **Chenyu** [[00:40:53](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2453)]
And if you have anything, you can just post it in the Fast Llama channel or something.
discover or anything you tried but didn't work.
I think those are helpful in some way.
OK, let's move on to UUVN stuff.

##### **Uuvn** [[00:41:32](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2492)]
Can you hear me?
Okay, so the old InfiniBand stuff that just averaged the gradients in the step works fine on three GPUs.
Each machine, three GPUs, two machines, total six GPUs in ResNet.
And it works fast, I think like one and a half times faster than just if I do this on one machine.
six gpus just doesn't work i think it's so it doesn't work deterministically on uh the same way i'm great 

##### **Chenyu** [[00:42:12](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2532)]
uh so you are saying three gpus on two machines each
It's faster than one machine with six GPUs?

##### **Uuvn** [[00:42:12](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2532)]
Six GPUs.
So if I have the same batch size across two machines, it's faster on ResNet.
And it works fine.
But it explodes.
And it does it deterministically.
So I think it's not related to InfiniBand.
And I tried just adding a bunch of sleeps everywhere.
Didn't fix that either.

##### **Geohot** [[00:42:44](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2564)]
Wait, wait, wait.
OK, OK, OK.
Let's slow down and let's structure this.
So in order to claim the bounty,
I expect three GPUs on each machine.
Six GPUs on each machine doesn't have to work.
But three GPUs on each machine does, and it should have speed very similar to six GPUs on one machine.
Is that where we are?

##### **Uuvn** [[00:43:04](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2584)]
Yeah.
Yeah, yeah, yeah.
That's the old implementation that is in cloud.
It's just like two processes that... Two processes, a bunch of changes in the data loader.
And inside of the step, average of the gradient.
So I exchange the gradients between two machines, average them.

##### **Geohot** [[00:43:22](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2602)]
Oh, wait, wait, wait, wait.
Hang on.
There should be no distinction from a tiny grad perspective if the GPUs are on the same physical machine or on two different physical machines, right?
Like the algorithm should be exactly the same.
I expect this to be byte for byte identical.

##### **Uuvn** [[00:43:39](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2619)]
So I'm talking about the old thing.
The new thing with Cloud that I'm currently doing, I haven't even got it working because I looked at the Cloud, thought that it's going to be easy, and it's not.
There is a lot of stuff that doesn't work.
There is five PRs open right now from me that fix some parts of it.
And yeah, I don't know where I'm going to port it to Cloud.

##### **Geohot** [[00:44:07](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2647)]
So I'm looking at these PRs and again, I'm seeing things that are like, they look to me like multiple changes.
Like don't hard code default cloud dev, right?
So there's a change there on line 169 that takes three lines and collapses it into one, right?
Like this is a white space change.
White space changes should never coexist with non-white space changes.

##### **Uuvn** [[00:44:29](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2669)]
OK, yeah, I can split that into separate PR.
Cool.

##### **Geohot** [[00:44:33](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2673)]
Like the PRs, they're too confusing for me to merge because there's too many things in there, right?
Like this PR is very contained.
It does this one thing.
So yeah, don't hard code default cloud dev.
Cool.
I understand what that does.
But the only change that should have is just the next device get available devices.
Why is multiprocessing current process.name equals main process being removed?
I'm talking about PR9935, and I see three completely different changes in there.

##### **Uuvn** [[00:45:10](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2710)]
Yeah.
Oh, I see.
So it was before I changed to next get.
So before I just changed that, it was in the global variable.
And for that, I had to set the multiprocessing name before starting process.
Otherwise, it would error because it didn't have the name main process.
So yeah, I forgot to revert that change.
I will split that.

##### **Geohot** [[00:45:37](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2737)]
Oh, so that got merged and shouldn't have gotten merged.

##### **Uuvn** [[00:45:40](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2740)]
What?

##### **Geohot** [[00:45:43](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2743)]
The cloud, the multiprocessing main process thing.
So that's in master right now and it shouldn't be there.

##### **Uuvn** [[00:45:49](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2749)]
Wait, what?

##### **Geohot** [[00:45:52](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2752)]
Are you saying the multiprocess, are you saying setting the name to main process is in master right now and it shouldn't be there?

##### **Uuvn** [[00:45:58](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2758)]
No, I'm saying the first iteration of don't-have-code-default-cloud-dev, this PR, did it differently.
And that required setting the name here instead of select.
You can see line 27 where- So you can revert something and make less.

##### **Chenyu** [[00:46:15](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2775)]
So you are saying you can revert something that still does what you want it to do, but it's like less diff.
You can revert part of that PR and still does what you want.

##### **Uuvn** [[00:46:28](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2788)]
Yeah, so I just forgot to... That's great.
Okay.

##### **Geohot** [[00:46:33](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2793)]
Yeah, no, but that should be, again, that should be a separate PR explaining this was added, it wasn't needed.
Oh, cool, merge, right?
The multiple cloud PRs open, I read them and I try to merge them.
But again, you really got to empathize with me here and think, is George going to understand what this is?
Is it one thing?
Because if I can't, I can't merge it.

##### **Uuvn** [[00:46:56](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2816)]
Okay, yeah.

##### **Chenyu** [[00:46:58](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2818)]
I think this is the same advice we will give any TinyGrad contributors.
It's a lot easier to merge 10 very small single focus item PRs than, I don't know, maybe like three PRs that try to save PR numbers or whatever, or because it's convenient to also change that.
That's never convenient for the reviewers to merge stuff.
It's a lot easier if you just split them up.
helps everyone and makes merging PR a lot easier.

##### **Uuvn** [[00:47:35](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2855)]
So the other thing with InfiniBand is that in order to do this.

##### **Geohot** [[00:47:42](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2862)]
Wait, wait, wait.
Let's stop and let's pause now.
And let's just focus on that.
Let's just focus on getting the Cloud stuff merged, simple PRs that I can just click Merge on.

##### **Chenyu** [[00:47:54](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2874)]
OK, yeah.
OK, read.
OK, so bug fix for PTX.
We broke it again after the linearizer refactor.

##### **Geohot** [[00:48:25](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2905)]
Wait, something broke from the linearizer refactor?

##### **Chenyu** [[00:48:26](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2906)]
I think it's because PTX.
not the best code, and it has a weird workaround that is easily broken.
OK.
Cool.
Can you add a test so that we at least know it's broken?
Or at least have something that indicates the state of this workaround.
It's a workaround.
We might want to remove it, but to have something that shows where we are.
Sure, then maybe just add TC=3 somewhere in the test suite.
It's fine to mark it as something wrong, but just add something.

##### **Geohot** [[00:49:23](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2963)]
Yeah, TC=3 should definitely be in the test suite.
I mean, again, when I did that linearizer refactor, the best I could do is just do all the tests and make sure the test passed.
It's hard for me to say, oh, there was this workaround and I have to go test that.
It's impossible.

##### **Chenyu** [[00:49:38](https://www.youtube.com/watch?v=-ayeO_SKx70&t=2978)]
Yeah.
I think this is, again, a general advice.
If you add something to TinyGrad and you want the maintainers to make sure that's correct, the best way you can do is add a test.
Test the behavior you want.
As long as it's like generic and not like a very specific test, I think it helps with future development speed as well.
Okay.
Other bounties.
Oh, comment on the FP8.
So I think I asked like, all in tinygrad.
Oh, in tinygrad implementation for Python backend.
I know it's lines.
I think, I don't know.
It can be made more compact.
That's probably fine.
But I made a comment that I don't understand why NaN is not supported.
I think it should definitely be supported because FP8 supports NaN.
And otherwise, I think that looks fine.
Either the author wants to make it compact, or if I merge it, I can probably make it more compact.
It's not a huge blocker.
We have people here working on stuff that I forget to mention.
If so, just post in general.
I don't think the metal multi-sync thing really fix it.
It doesn't fix on benchmark, and the test is already passing on master.
So I don't understand that.

##### **Geohot** [[00:51:31](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3091)]
Oh, if it doesn't fix it on benchmark, then that's where I wanted to re-enable it.
If that thing doesn't fix it.
I don't really understand.

##### **Chenyu** [[00:51:39](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3099)]
The author re-enabled it, but I run it on benchmark, it failed.

##### **Geohot** [[00:51:45](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3105)]
Yeah, OK.
I don't know.
Maybe that's just a bad bounty.
A bunch of people have put stuff for that.
But if there's no way for people to verify it, then it can't really be a bounty.

##### **Chenyu** [[00:51:56](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3116)]
I mean, the way to verify it is they just re-enable it, and we run on benchmark, and that's correct.
And we understand why it wasn't correct.

##### **Geohot** [[00:52:06](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3126)]
Yeah, because if this doesn't work, this is the exact problem that I want to fix.
OK, cool.

##### **Chenyu** [[00:52:12](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3132)]
For the Z3 stuff, I see good progress.
I also see Qazalin discussing things with lykos on the PR.
My only issue was there are some rules in the grouper that I don't think they should be part of that.
Otherwise, I think the Z3 part and check out of bound, basically rewriting our uop expressions for index into Z3, I think those are good directions we want to see.
So that part looks good to me.
Pretty much it.

##### **Geohot** [[00:53:10](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3190)]
I wanted to briefly talk about, yeah, the Tenstorrent and bounty.
What I want to see in order to get that bounty lock is all of the ops tests passing, and in such a way that doesn't, like, you can't just only use one core.
Like, you have to use, you have to, in theory, your approach has to scale to the entire chip.
All model tests don't need to pass in order for the lock to claim the bounty you do, but just for the lock, just get ops passing.

##### **Chenyu** [[00:53:42](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3222)]
and no limits on making fast as long as it's correct?

##### **Geohot** [[00:53:48](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3228)]
Yeah, I don't think we're going to.
With the speed thing, it's like, if there's something deeply broken about your approach that will never, ever get speed, then no, that's not OK.
But if it's just like, oh, well, I didn't add support for the Tenstorrent Tensor Cores, yeah, I think that's fine.

##### **Chenyu** [[00:54:15](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3255)]
Yeah.
I think that's pretty much it.
I think that's work.

##### **Geohot** [[00:54:30](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3270)]
Nope.
I'm going back to sleep.
I still feel awful.
It's hard to think with a fever.

##### **Chenyu** [[00:54:35](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3275)]
OK, take care.
I'll take care.
Thanks, everyone.
See you next week.

##### **Geohot** [[00:54:42](https://www.youtube.com/watch?v=-ayeO_SKx70&t=3282)]
See you all next week.
