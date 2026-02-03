# 2025-09-08 Meeting

### Meeting Agenda

**Time:**  9am Monday San Diego time
- company updates (new meeting time?)
- make rangeify default, speed regression/bug
- ci speed
- MLPerf LLaMA
- viz tool
- cpu thread
- symbolic
- cloud

### Audio

[Youtube Link](https://www.youtube.com/watch?v=5-0CYqlEE2c)

### Highlights

- **[Company Update](#geohot-000006)**: The price of the TinyBox was lowered to $25,000, resulting in six new orders. The price may return to $29,000 if sales volume doesn't persist. The meeting time will remain the same for the next three weeks while Geohot is in Asia.

- **[Rangeify as Default](#geohot-000147)**: `post-op` is now the default, which moves the optimizer to run after the `lower` pass. This is a key step towards making `rangeify` the default. Geohot will focus on implementing a cost function for `rangeify` to manage the trade-offs between compute, storage, and locality. The ultimate goal is to enable `rangeify=1` by default and delete over 1,500 lines of legacy code related to `ShapeTracker`.

- **[CI Speed](#chenyu-000905)**: The CI pipeline is still slow, running at about seven minutes. The team discussed profiling tinygrad to find bottlenecks, identifying and potentially removing tests that have low value, and refactoring tests (e.g., tensor core tests) to be cleaner unit tests. They agreed they are using too many GitHub workers, which negatively impacts developer experience on forks.

- **[MLPerf LLaMA](#chenyu-001615)**: A training run is converging but is too slow to be a competitive MLPerf submission. The current run is on a 1K context length, while the benchmark requires 8K. The team also discussed ongoing hardware instability with the MI300 machines and plans to consolidate working GPUs into one stable machine.

- **[Viz Tool](#qazalin-002117)**: Work is in progress to improve the visualization tool's performance by implementing a range tree for rendering, which will provide a significant speedup. Geohot highlighted remaining UI glitches and requested better cancellation logic for large graph rendering. A future goal is to integrate memory planner visualization, linking memory buffers in the profiler back to the schedule graph.

- **[CPU Thread & Driver](#nimlgen-003047)**: The CPU threading implementation has been merged. A key task is to optimize the slow loading of Stable Diffusion weights by reading the entire file into memory at once and using buffer views. The team also discussed a recurring NVIDIA driver issue on CI machines that requires a system reboot after several non-graceful shutdowns.

- **[Symbolic](#siedslykles-003922)**: The `dtype_index` feature was merged, and work is underway to add the `invalid_index`. This introduces a new symbolic `dtype` for indices that includes an `invalid` value. Loading from an `invalid` index returns zero, and storing to it does nothing. This provides a more flexible and composable way to handle masks and padding at a higher level of abstraction.

- **[Cloud & Infrastructure](#wozeparrot-004516)**: The old machine provisioning system is being deprecated in favor of the new cloud infrastructure. The physical server room has been upgraded with better insulation and fans for climate control. A plan was made to deploy telemetry to all company machines to better monitor their status and uptime.

- **[Bounties](#hooved-004659)**: The BERT training bounty is ongoing, with a run in float32 to ensure convergence before switching to BF16. Geohot is paying out the bounty for `merge_assign_and_store` and has posted a new $800 bounty for implementing Winograd convolution as a rewrite rule.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=0)]
Let's get started. Let's start with company update.

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=6)]
Yeah, so we lowered the price to $25,000. We got six orders for greens and we sold the last red. Yeah, so three of those orders have paid. We're making a lot of money now, but we're making less profit margin. So, yeah, I don't know. I think we'll keep it at, if sales stay like this, we'll keep it at $25,000. Otherwise, we'll put it back to $29,000. We make like, the boxes cost about $20,000 to make. So, you know, you want to make $5,000, you want to make $9,000. It was nicer to make $9,000, but if we're going to sell more than double as many boxes, I'd rather make $5,000.

##### **Geohot** [[00:00:50](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=50)]
So, yeah.

##### **Hooved** [[00:00:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=56)]
Okay.

##### **Chenyu** [[00:01:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=60)]
We adjust meeting time next week?

##### **Geohot** [[00:01:04](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=64)]
Yeah, so I'm going back to Asia today. What time is it now in Hong Kong? Midnight.

##### **Chenyu** [[00:01:12](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=72)]
Yes. Will you be available next week?

##### **Geohot** [[00:01:18](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=78)]
Yeah, I'll be here for the meeting next week. I don't know, I could just do it at midnight. I'll be out for the meetings, the two meetings after that, and then we'll all be in Hong Kong together.

##### **Chenyu** [[00:01:29](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=89)]
Okay, so let's keep this time for the next three weeks, then we will adjust after most people are in Asia.

##### **Hooved** [[00:01:36](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=96)]
Cool.

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=99)]
Cool. Sounds good.

##### **Chenyu** [[00:01:42](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=102)]
Okay, next is, make rangeify default.

##### **Geohot** [[00:01:47](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=107)]
So not rangeify, I made post-op the default.

##### **Chenyu** [[00:01:51](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=111)]
Yes, I mean, that's the main goal.

##### **Geohot** [[00:01:54](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=114)]
Yeah. Yeah, so post-op is a requirement to, so now it works with rangeify. If you set rangeify equals one, you'll now get optimized kernels instead of unoptimized kernels. We had to basically move the optimizer after the rangeification. So like kernel.py had tons of references to shape trackers and shape trackers going away. So this was kind of the first step. I'm glad it finally got merged last week, even if there are some minor regressions. The, this will also let us do a whole bunch of other things. I have the PR up. I don't know if your tests are failing. I have to look into why. But we could move the reduce collapse, like the A range reduce collapse, to before optimizations. We could do a lot of stuff before we run the optimizer, because now, like the optimizer runs after the lower. So we couldn't do things like the.. Reduction of A range until we ran the lower, and we couldn't run the lower until we ran optimizations. But now we can do that. So yeah, that changes. And then the main thing that I have to work on for the next couple of weeks is the cost function in rangeify. So there's an implicit cost function in the scheduler about when you want to do.. There's always a trade-off between basically.. I don't know.

##### **Hooved** [[00:03:24](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=204)]
I don't know.

##### **Geohot** [[00:03:25](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=205)]
Compute, storage, and locality. These things are like three points on a triangle. So like compute and storage is an obvious trade-off. You can either.. You want to have A times two? Well, you can either.. You use A times two twice, right? You already have A stored. You can either recompute A times two both times, or you can store A times two and load from it. And in that case, it's probably always worth it to recompute. But you have to have a cost function here, because these things get more complicated. And then you have this locality trade-off, which says basically the.. Like, all storage is not created equal. If you are going to store something and use it right away, this is a lot less bad than having to store basically like A and A times two for the entire duration of the whole graph. Right? Like if you need A and A times two for the backward pass, you should definitely be recomputing. A times two over by the backward pass. I think there was a.. I forget what the name was for this. There's a name for like.. You can store a lot..

##### **Chenyu** [[00:04:40](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=280)]
Gradient accumulation? Gradient checkpointing.

##### **Geohot** [[00:04:45](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=285)]
Gradient checkpointing. Yeah, yeah, yeah. Yeah, gradient checkpointing. So gradient checkpointing is a form of this trade-off about locality. So, and then this locality trade-off also persists at.. The really nice thing about this stuff and getting it right is it's identical at every layer. So everything that we want to do at the global layer also applies at the local layer, also applies at the register layer. So yeah, hopefully when we get the formulation of this stuff correct, it will all kind of fall into place. I read the Triton paper this weekend. About their.. It's interesting. They don't like.. Nothing I've read seems as good as Rangeify. Like, the Triton paper is talking about how they're representing their shapes in this. Kind of like what we do with TensorCore. They divide everything up into.. They make every axis a two. And then you can flip all your twos around, right? And then this is a linear transformation. To move your twos around. And then all these things can be expressed as linear transformations. Like a reshape and a permute. Yeah, so.. But it's still like.. They still have this concept of reshape and permute. I feel like that should be dealt with at an earlier level. Instead of doing the reshape and the permutes on your layout, which is what the ShapeTracker was doing. You can do this on.. I mean, I guess it's still your layout, but it's at the bufferize. It's only the layout in the.. In memory. That you're optimizing. It's not this like nebulous idea of a layout. There should be no.. Like, if you have something that's like.. Plus one. If you have something that's like buffer, plus one. Permute, plus one. This is ridiculous, right? There's no reason at all you should store that middle one. Because you can just load from it permuted. So the old way we used to think about this was pushing the permute. But forget pushing the permute. Just think about what the actual.. What the actual ranges are of these things. And realize that the two plus ones are element-wise ops on the exact same ranges. So. Yeah. I think it's.. I think it's good. I've now read all the.. The Halide and the TVM. And see how they do this kind of stuff. I mean, it is.. They have a very like range-ified view of things. TVM has really nice syntax too. Like TVM lets you.. Most things in TVM.. And I guess Halide too. Are.. Are.. Are.. Are.. Are.. Are.. Like you can like.. You want to permute. You can say.. B sub i comma j equals a sub j comma i. And I feel like that's like a really nice syntax. So.. I'm going to work on that syntax. I'm going to work on the range-ified cost function. And then.. A bunch of cleanup still around post-opt. Fixing this pad too. If there's speed regressions. And if there's..

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=470)]
Bugs. Yeah. Yeah.

##### **Chenyu** [[00:07:54](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=474)]
What are the blockers? Before we can start to delete more stuff?

##### **Geohot** [[00:07:59](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=479)]
So.. We have to switch to range-ify as the default. Try range-ify on stuff. It is really slow. Because it is storing pretty much everything. So.. Yeah.

##### **Chenyu** [[00:08:11](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=491)]
Or some sensible cost function to start with.

##### **Geohot** [[00:08:14](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=494)]
Yep. Make range-ify equals one the default. And then once range-ify equals one is the default.. We can delete a ton of stuff. Right. There's probably a good.. 1,500, 2,000 lines we can delete.

##### **Geohot** [[00:08:29](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=509)]
Like every.. Like half of it.

##### **Chenyu** [[00:08:31](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=511)]
Every time I heard.. Something like this.. My mental discount is like 30%. Hey, post-op deleted lines? I mean, that's something to start with. But sure.

##### **Geohot** [[00:08:44](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=524)]
Yeah. No, look. Look, range-ify is already using 500 lines. Right? Like we've already added 500, 600 lines. It's not like it's.. It's nothing. Yeah. Yeah. Yeah. Those lines are already paid for, so..

##### **Geohot** [[00:08:55](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=535)]
Oh, yeah. Okay. Great. Cool. Anything else? Nope.

##### **Chenyu** [[00:09:05](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=545)]
Okay. Next, it's CI speed. That's where you can spend some time staring at the tests. And I think now it's like 30 seconds faster, but most stuff are still slow. Let me do something about it.

##### **Geohot** [[00:09:23](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=563)]
I think now it's like seven minutes.

##### **Geohot** [[00:09:26](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=566)]
I mean, I just deleted a whole bunch of..

##### **Chenyu** [[00:09:29](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=569)]
I just like.. But those are not the slow ones. Those are like annoying ones to maintain, but not the slow ones.

##### **Geohot** [[00:09:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=577)]
Yeah. I don't know. We should just figure out.. Like, OpenPilot spent a lot of time just figuring out which tests ever actually caught failures. And then kind of like looked at all these other tests that like.. What I would love to have is something that goes back to our entire history and says, Okay, which tests have ever failed?

##### **Geohot** [[00:10:04](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=604)]
Uh, I mean..

##### **Chenyu** [[00:10:07](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=607)]
I hope the test was added initially because it.. Some kind of regression test?

##### **Geohot** [[00:10:13](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=613)]
Yeah, maybe. But like, I'm wondering if there's some like long tests that we already basically have full coverage of. Uh.. Where we're just like doing extra stuff. I don't know. I mean, also, it's been a long time in general since anyone sat down with a profiler and just looked at like what's slow in TinyGrad. I have that PR'd or not run hand-coded optimizations twice, but for some reason it's changing things. So like little things like that. I think if we just like sat down with a profiler, I bet we could make everything a lot faster.

##### **Chenyu** [[00:10:48](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=648)]
I think also some back-end.. Or maybe it's just our setup. Yeah, I think some of the tests are very slow. I think Envy is one notable example. That's kind of slow. OpenSVU is also kind of slow.

##### **Geohot** [[00:11:01](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=661)]
I put a lot of time into this. Envy's environment setup is one minute.

##### **Geohot** [[00:11:07](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=667)]
Okay. And the man-test takes like seven. Wait, which one is what?

##### **Sieds Lykles** [[00:11:15](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=675)]
Envy usually always takes the longest. For some reason. I think, yeah, just the byte test is just slow on Envy.

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=682)]
Yeah, GPUOscillaut. Yeah, GPUOscillaut is not that fast. Right, like this is going to be more of a thing of saying like we actually already have enough coverage on these things.

##### **Geohot** [[00:11:34](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=694)]
The problem is we don't really because that's the only test we got. Yeah. I don't know. I mean, setEnvironment.. Like we've put a lot of time into this.

##### **Geohot** [[00:11:52](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=712)]
I don't know how much faster it's going to get.

##### **Chenyu** [[00:11:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=716)]
Yeah, I mean, one solution is always like break down further. But now you use a lot of workers. And for anyone who is on their fork that doesn't have, doesn't pay for the workers,

##### **Geohot** [[00:12:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=728)]
it's very slow. We're already using way too many workers. It was kind of a mistake. It was kind of a mistake. I bought us a nice GitHub account and now we have too many tests. So I don't know.

##### **Chenyu** [[00:12:21](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=741)]
Yeah, we just need to keep going. We need to like make decisions. My issue is I run tests on my fork and if I have like three sets of stuff on my fork, it takes like half an hour to catch up. It's very annoying.

##### **Geohot** [[00:12:32](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=752)]
You can use a company credit card and buy a better GitHub account if you want.

##### **Chenyu** [[00:12:36](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=756)]
But it's not for me, right? It's for potential people who will be working on this. That's developer experience.

##### **Geohot** [[00:12:42](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=762)]
Yeah. I don't know. We should just delete a lot of these tests. Okay. Yeah.

##### **Chenyu** [[00:12:49](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=769)]
Probably continue consolidating something. If we all agree we are using too many workers now.

##### **Geohot** [[00:12:55](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=775)]
If we all agree we are using too many workers now. No, we're definitely using too many workers. It's going crazy. Great. And there's a bunch of things like tensor core tests. I refactored them a little. At least I made emulate not be like emulate underscore metal. But like tensor core tests should be refactored. But like tensor core tests should be refactored. Why is this a separate thing? There should just be a unit test There should just be a unit test that tests all the tensor cores in emulation.

##### **Chenyu** [[00:13:21](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=801)]
Oh, isn't that what's currently being done? Python backhand runs these as unit tests?

##### **Geohot** [[00:13:26](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=806)]
That doesn't run as a unit test, like we have a special worker called tensor core Tests. Uh and it makes tons of calls to different stuff, when this should just Like it makes tons of calls to Python. Where as this should just be like a unit test. None of this stuff is running parallaly. So we should look for places where where we're not using our testing framework. Every time we're calling some arbitrary piece of Python, this is always how things break, too. Everything should just be in test. If we only want it to run on one device, it should be in unit, and then that. I think also we might be able to migrate a bunch of stuff to unit, for things that are clearly..

##### **Chenyu** [[00:14:11](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=851)]
So that's another thing I have been adding, and now unit is very big, such that metal unit is getting slow. Which unit is slow? Metal unit as a whole is slow. Metal unit. Do we have a metal unit? Yeah, I think unit's running on metal, and..

##### **Geohot** [[00:14:32](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=872)]
Oh, you mean Mac OS? Yeah, Mac OS. Well, we call something Mac OS unit, but it has a ton of random crap in there. Yes, so we definitely have something that needs to be split up, and something that can be merged out again. In fact, this doesn't even look like it's running the unit test. No, it's running PyTest. We call it PyTest, though. Well, no, but it runs PyTest for AMD and stuff. Oh, that's the other stuff. I'm looking at Mac OS unit, and it looks like this doesn't actually run the unit test.

##### **Chenyu** [[00:15:05](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=905)]
Great. Yeah.

##### **Hooved** [[00:15:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=908)]
Anyway.

##### **Geohot** [[00:15:09](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=909)]
This is what I mean. Those YAML files are not the place to put things in. All of that logic needs to be.. moved to PyTest.

##### **Geohot** [[00:15:19](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=919)]
Okay. Anyway. Yeah. There's way too much.. There's way too much, like.. Yeah. Oh. Yeah, we just need to.. Move lots of stuff to unit, and just start deleting stuff.

##### **Geohot** [[00:15:38](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=938)]
Make sure unit's actually working really well. Yeah.

##### **Geohot** [[00:15:44](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=944)]
Yes.

##### **Geohot** [[00:15:45](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=945)]
Like, we have something called unit tests, which is really fast, just called unit tests. And then it also spends time running SDXL on null backend. Do we want that?

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=955)]
I don't know. I'd probably put it in and delete it.

##### **Hooved** [[00:16:01](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=961)]
OK.

##### **Geohot** [[00:16:02](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=962)]
I'll think about it.

##### **Chenyu** [[00:16:03](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=963)]
Also, another thing is, if something can fail, we want it to fail earlier. So ordering of these stuff will also help.

##### **Hooved** [[00:16:12](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=972)]
Cool.

##### **Geohot** [[00:16:13](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=973)]
OK.

##### **Chenyu** [[00:16:15](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=975)]
So, Nexus, MFperf, LLaMA. I don't think we really have anything. Wolfsparred, how's your run going?

##### **Wozeparrot** [[00:16:23](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=983)]
The run is still going. We're at, like, 3.56 eval loss. So it seems to be convergent on schedule.

##### **Chenyu** [[00:16:33](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=993)]
3 days?

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=997)]
It is after 130 hours. You got a WAN DB link? No weights and biases tracking on this run. OK. I don't think.

##### **Chenyu** [[00:16:49](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1009)]
I think after certain steps, it's not really worth it to just run. I don't know. Because realistically, if one AB training run takes, like, seven days, we are not going to make it to MFperf anyway.

##### **Geohot** [[00:17:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1028)]
Yeah.

##### **Chenyu** [[00:17:09](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1029)]
So I feel like it's not worth it to really, I mean, it costs power or something.

##### **Geohot** [[00:17:13](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1033)]
Yeah.

##### **Hooved** [[00:17:14](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1034)]
Yeah.

##### **Geohot** [[00:17:22](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1042)]
But it's also worth it to make it to MFperf. I don't know. I really didn't do much about fusing stuff.

##### **Chenyu** [[00:17:29](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1049)]
We don't want to use fuse if the goal is to make branch by default.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1062)]
So fuse is.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1062)]
I mean, fuse should work in Ranger 5 probably too.

##### **Chenyu** [[00:17:49](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1069)]
Yes. But it's kind of a, it should just work and not, like, messing around with fuse in the front end.

##### **Geohot** [[00:17:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1076)]
Yeah. OK. I'll start working on the cost function this week, and we'll know pretty quickly if that's just going to work. Yeah.

##### **Chenyu** [[00:18:03](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1083)]
So I think that would be best. Otherwise, I mean, if we cannot something, anything that's wrong, it's probably fine.

##### **Hooved** [[00:18:11](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1091)]
Hm. Yeah.

##### **Hooved** [[00:18:12](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1092)]
Yeah. OK.

##### **Geohot** [[00:18:13](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1093)]
It's just too slow? Like, even 8B is way too slow?

##### **Chenyu** [[00:18:17](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1097)]
So first, this is just context 1K. The benchmark is 8K. We need to get there first. But even 1B looks very slow now.

##### **Hooved** [[00:18:26](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1106)]
OK.

##### **Geohot** [[00:18:30](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1110)]
OK. I don't really have anything else to add.

##### **Chenyu** [[00:18:38](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1118)]
Other than, when do we plan to do this? We plan to upgrade LLVM or Rock M7 or whatever. The MI300 machine has been, AMD2 is pretty broken.

##### **Wozeparrot** [[00:18:57](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1137)]
I can see what's wrong with AMD2. I took a look already, but it's kind of weird. Almost seems hardware related, but.

##### **Chenyu** [[00:19:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1148)]
So it might be hardware related. The issue I was encountering was, like, the hardware. Basically, you would train it for an hour, then one GPU crash or something, then the whole thing hangs, then I need to reboot or something like that.

##### **Geohot** [[00:19:23](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1163)]
Yeah, I can bump Rock M on it and see if it helps.

##### **Geohot** [[00:19:29](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1169)]
So GPU3 in AMD1 seems something's wrong with that. I think we've seen a couple times it gets into this state with a voltage regulator over temperatures. I don't know. We should probably swap that. We should probably swap it with one of them in AMD2. We should be able to carefully swap the GPUs between machines. I don't know, maybe we're only going to get one working one. Or, I don't know, we can send it back to AMD and complain. But yeah, we should at least update to the latest stuff and put some effort into trying to root cause what's going on. How about the 350 machines? Are they better? Yeah, the 350 has been really stable. Great. Yeah, the 300 machines look like they were used from somewhere. The 350 machines looked better.

##### **Geohot** [[00:20:22](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1222)]
Maybe I will migrate to the 350.

##### **Geohot** [[00:20:26](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1226)]
But yeah, we can definitely make one good 300 machine out of the two. I think we should just swap GPU3 and tinyAMD1. Yeah, I mean, if that's the case, I will hope to use that good machine.

##### **Chenyu** [[00:20:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1237)]
Yeah, yeah, definitely. Cool. Okay. Sounds good. Other than that, no real update on LAMA.

##### **Geohot** [[00:20:47](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1247)]
So let's move on to this. Is it good now? Yep. Great.

##### **Qazalin** [[00:21:17](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1277)]
I'm working on the fast algorithm that's still in the branch. The basic idea is to just make a tree instead of the data structure that we currently have, which is a list, and do a range query on that tree. That should be pretty fast. Yeah, I think the data structure is already through some of the.

##### **Geohot** [[00:21:43](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1303)]
It's a range tree, right?

##### **Qazalin** [[00:21:47](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1307)]
Yeah, pretty much a range tree. Like do a binary search on it, then.

##### **Geohot** [[00:21:51](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1311)]
Great.

##### **Qazalin** [[00:21:52](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1312)]
complexity. Time to merge this week. I had a bunch of fun going through the NVIDIA tools, seeing what they do in Profedo. Hmm. I think I'm trapped. I'm trapped to merge it. Still with the.

##### **Geohot** [[00:22:16](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1336)]
Great. Yeah, I mean, it should be really responsive.

##### **Geohot** [[00:22:23](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1343)]
I'm hoping this isn't like a tiny improvement. I'm hoping this is like a massive, like, big old notation improvement.

##### **Qazalin** [[00:22:33](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1353)]
It will be, because right now we are all of n. On every single zoom. And that's very high overhead. The other problem is that we're just drawing too many stuff, especially on Firefox. It's interesting how much faster Chrome is than Firefox with the canvas.

##### **Geohot** [[00:22:52](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1372)]
Oh, interesting. Yeah, I use Firefox.

##### **Geohot** [[00:22:58](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1378)]
It should be good. It's got to be good on Firefox.

##### **Qazalin** [[00:23:04](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1384)]
Yeah. That's right. I try to make things faster. I use browsers to make things fast. Safari is the worst. I try. Yeah.

##### **Geohot** [[00:23:16](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1396)]
Yeah, I mean, I still get like some glitchiness sometimes. Like, for example, if I click on a big graph and then I click back to the profiler, it still says rendering new graph at the top.

##### **Geohot** [[00:23:28](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1408)]
And then it eventually, like, snaps me to that graph.

##### **Geohot** [[00:23:38](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1418)]
Right, like here, I'll paste a screenshot. Like right now, I'm selected on profiler, but there's clearly not a profiler in the main view. I think we've talked about this before, but I would really like this bug to be root-caused. Got some like web worker coming in async or something?

##### **Geohot** [[00:23:58](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1438)]
I think so, yeah.

##### **Geohot** [[00:24:02](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1442)]
Yeah, I mean, that's one of the last bits of like real jankiness I find. I think in general, just working on improving the big graph cancellation stuff. Like, okay, I click on something that's really big, and then it lags, and it should never lag. It's okay if it doesn't render it, but it should never lag.

##### **Geohot** [[00:24:31](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1471)]
Now I'm in some locked state. I think the other thing to start thinking about, too,

##### **Geohot** [[00:24:51](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1491)]
is how we want to move the memory planner

##### **Geohot** [[00:24:58](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1498)]
into something that Viz can use to do that. Can visualize? Like how.. When we have like buffers in the memory graph,

##### **Geohot** [[00:25:16](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1516)]
how do we link that back to the schedule graph? Like, can I click on a buffer in the memory graph, and it does anything?

##### **Qazalin** [[00:25:26](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1526)]
It does that. Yeah, it's very hard to trace it back. Back to the actual kernels. Stuff can be reused for other stuff.

##### **Geohot** [[00:25:38](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1538)]
Yeah, like the same way that we click on the kernel, I want to click on the memory, and I want it to do something intelligent.

##### **Geohot** [[00:25:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1556)]
Yeah, you'd want to like tie..

##### **Qazalin** [[00:26:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1560)]
Basically backtrack from the buffer objects to the kernel to exactly the back to the original bitrate.

##### **Geohot** [[00:26:09](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1569)]
Yeah, like maybe if I click on it, and maybe you can make this only work on range of five. It's easier. Like when I click on it, it should go to.. Well, so I like now that we have this concept of lighting up a UOp. So like imagine when I click on the memory, it takes me to.. Well, I guess it could be in multiple schedules. Like imagine it takes me.. It takes me to the schedule, and it's lit up as the buffer object.

##### **Qazalin** [[00:26:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1597)]
You could like navigate through different uses of that buffer, like the read and the write.

##### **Geohot** [[00:26:46](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1606)]
Yeah. I mean, it would also.. In a schedule, it will only show up once as an object. It's called a buffer. Multiple.

##### **Qazalin** [[00:26:58](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1618)]
Multiple reads. That's a buffer interface. That's a buffer.

##### **Geohot** [[00:27:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1620)]
Well, yeah, but that should just be like.. Again, that should just be the object. That should be like that UOp in the schedule lit up, right? Multiple reads are just multiple outgoing arrows. But yeah, like when I view tensor graph in the schedule, there's something called buffer. And yeah, like that's what I want to be able to get to from the profiler. Yeah. When I click on it, it takes me to the schedule with the buffer lit up. But it may be in two schedules, so we need some way to navigate between schedules.

##### **Qazalin** [[00:27:42](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1662)]
And then you'll have the complication of something is memory planned and in the JIT. So there's like no way to actually know what's going on. There's this big blob in the beautiful endless graph.

##### **Geohot** [[00:27:54](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1674)]
Yeah. I mean, we have to move.. We have to move the memory planner.

##### **Geohot** [[00:28:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1680)]
To the schedule. With buffer view ops? Yeah. Buffer view ops should be fine. And it's okay if it's like one big buffer and it just has buffer view ops. Like that's okay. If that's really what it is, then that's what it is. But cool. Speed.

##### **Geohot** [[00:28:25](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1705)]
The bug. The glitchiness. Just click around. Click around. And if you could somehow break Viz, you're not done. Keep clicking around until it breaks. Then we can click around and say, all right, I'm confident it doesn't break. I'll click around and it'll break. And then.. Yeah. And then the memory's done.

##### **Qazalin** [[00:28:44](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1724)]
Yeah. There's.. I fixed the resizing bug this week. Hopefully. The bugs will be fixed.

##### **Geohot** [[00:28:51](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1731)]
Cool. Yeah. A lot of compliments on Twitter for Viz. People are like, wow, TinyGrad really has a.. Yeah. Best visualizer for this stuff I've seen.

##### **Qazalin** [[00:29:02](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1742)]
I tried using NVIDIA's tools. It's very good. It's just so hard. I have to set up so much stuff. Yeah.

##### **Geohot** [[00:29:09](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1749)]
No, I mean, the tools are great. But the only people who use them are the highest-end engineers at OpenAI who can.. The highest-end engineers doing these kernels can do it, but they're not usable by any sort of casual ML person. Yeah. We're designing tools. We're designing tools for the ML researcher, not the.. I've devoted my entire career to NVIDIA.

##### **Qazalin** [[00:29:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1777)]
They also have godly amounts of patience.

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1782)]
For what? What's slow?

##### **Qazalin** [[00:29:47](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1787)]
The workflow of triggering the profiler and then viewing the trace is many, many clicks.

##### **Geohot** [[00:29:55](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1795)]
Yeah.

##### **Geohot** [[00:29:57](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1797)]
I mean, that's been.. That's been..

##### **Geohot** [[00:29:58](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1798)]
Yeah. Right.

##### **Geohot** [[00:30:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1800)]
That's been my experience with this stuff, too. Like, it's just.. You're.. Of the.. All the people who use NVIDIA, only 3% of people use these profilers as part of their workflow. Maybe, like, 50% of people have tried the profiler once, and they're like, this does not provide enough value for how much effort I'm putting into it. So, yeah. That's why you always want to be on that trade-off.

##### **Geohot** [[00:30:27](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1827)]
Cool. Thank you. Thanks. Next is CPU thread for driver. Yeah. So, threading is merged.

##### **Nimlgen** [[00:30:47](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1847)]
So, actually, LLaMA with CPU floating looks better now. Yeah. So, it looks better. I still see some issues on 350, so I'm going to look this week. So I know what's causing that, but I don't think it's hardware, maybe it's our driver. So yeah, I'm going to look into this. Just 300 is fine.

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1881)]
Can you look into why loading the weights for

##### **Nimlgen** [[00:31:24](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1884)]
stable diffusion is so slow? Yeah, I took a look and the whole time now spent in schedule, like it's not in the run time.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1896)]
I see. I mean,

##### **Geohot** [[00:31:41](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1901)]
can you like, ideally the way I want to do this is I want, like right now, ideally what I want to do with all of these things is just load the file, however it is off of the disk. Like I want the disk load to RAM to be super fast. You're going to be using all the weights anyway. So the disk load to RAM should just be like one solid disk load and then just buffer views for everything.

##### **Geohot** [[00:32:12](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1932)]
Can you switch it to that and profile that? You see what I mean by that, right?

##### **Geohot** [[00:32:20](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1940)]
Yeah. Yeah, because we should be getting, we should never, the speed of loading should never be dependent on how many tensors there are in the file. Right? Like if the file is four gigs, great, it should load at however many gigs per second we can get with this maximum throughput pipe of you know, DMA from the drive as best as we can and then just slice it up and use the buffers to slice this.

##### **Chenyu** [[00:32:49](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1969)]
So just add a contiguous after your two or something like that.

##### **Geohot** [[00:32:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=1976)]
Yeah, contiguous after. Or two copies to be contiguous. Yeah. Yeah, just copy it off the disk. But cool, yeah. So switch to that and then just profile that.

##### **Geohot** [[00:33:20](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2000)]
Oh, and also the CPU and LLVM refactor. Yeah. Yeah. So the CPU and LLVM are like refactoring these things to like, I just imagine the device taking a tuple for like device, for like compiler render.

##### **Geohot** [[00:33:35](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2015)]
Yeah.

##### **Nimlgen** [[00:33:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2017)]
Yeah. Actually, I thought it that, so the only problem is that we have function like special LLVM function in tensor to pi, which is, I don't remember how it's called, something with b. It's called bfloat16. I think that is true. Yeah, LLVM bfloat16.

##### **Chenyu** [[00:33:59](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2039)]
Yeah, that probably needs to be fixed somewhere else, like in a different way anyways. So if that's a blocker, you're free to just remove that.

##### **Geohot** [[00:34:10](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2050)]
Yeah, okay. Yeah, because that was,

##### **Chenyu** [[00:34:17](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2057)]
that cast was kind of there, because we don't support bfloat16 on many of the backends.

##### **Hooved** [[00:34:24](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2064)]
So I guess that's why we need to do something like this. Yeah. I think that's a good point, because it's not just like,

##### **Chenyu** [[00:34:25](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2065)]
no most of it is supported kind of, and we don't really want to do that in the frontend.

##### **Geohot** [[00:34:32](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2072)]
Yeah, that should be in decompositions. If there's bfloat16s leftover,

##### **Geohot** [[00:34:38](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2078)]
it should be in decompositions to remove them. Okay.

##### **Hooved** [[00:34:47](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2087)]
Yeah.

##### **Geohot** [[00:34:51](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2091)]
Also, I should have some of these by the time we're in Hong Kong. These are the ones that are in the backend. These are the Comma GPU board.

##### **Geohot** [[00:34:59](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2099)]
And the big advantage, we have a UART. Mm-hmm, yeah. So we'll finally be able to debug that firmware without the USB goes down, and then we don't know what happened. Cool, yeah. Yeah, I'll try to bring some of these boards.

##### **Hooved** [[00:35:29](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2129)]
Okay.

##### **Geohot** [[00:35:32](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2132)]
Huh? Anything else? No. I also will try to do something with NV,

##### **Nimlgen** [[00:35:40](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2140)]
but, yeah, I suppose that that's unrelated to the cards. So yeah, and the reboot is the only option.

##### **Geohot** [[00:35:49](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2149)]
I mean, other people are experiencing that too.

##### **Nimlgen** [[00:35:55](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2155)]
Yeah, actually, the workaround for them is just to disable everything, like the driver and something like that. So they just don't reset the GPU at all. But we just need to reset GPU in some cases. So yeah.

##### **Geohot** [[00:36:14](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2174)]
Yeah, NVIDIA needs to fix this. So right now, if it ever isn't being gracefully shut down,

##### **Geohot** [[00:36:28](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2188)]
we have to reboot the machine?

##### **Nimlgen** [[00:36:31](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2191)]
Not every time. I know like six or seven times, it's fine. But after that, yeah. I know it's just it depends.

##### **Geohot** [[00:36:41](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2201)]
Deterministically six or seven, or is it like R&D?

##### **Nimlgen** [[00:36:44](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2204)]
Around that.

##### **Geohot** [[00:36:45](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2205)]
Like maybe five. Four.

##### **Hooved** [[00:36:47](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2207)]
Oh.

##### **Geohot** [[00:36:48](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2208)]
So it's like R&D. It hits 20% of the time or so?

##### **Geohot** [[00:36:52](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2212)]
Yeah. All right. Yeah.

##### **Geohot** [[00:36:57](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2217)]
Yeah, I think maybe what we should do is add, can you detect if it's in the bad state, and then just have it reboot the machine in the CI job?

##### **Nimlgen** [[00:37:07](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2227)]
I didn't know yet.

##### **Chenyu** [[00:37:09](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2229)]
Oh, speaking of this, Wolf Perry, do you have some telemetry tracking on the CPU? The TinyBox machine?

##### **Geohot** [[00:37:21](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2241)]
Yes. You can see them on stats? Yes.

##### **Chenyu** [[00:37:26](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2246)]
Maybe let's start with adding those to some bot channel similar to our CI channel so we can at least see those and something about it.

##### **Wozeparrot** [[00:37:42](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2262)]
But like what telemetry? Let's see. Let's start with the machine that's on or rebooted. I don't know.

##### **Geohot** [[00:37:49](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2269)]
I collect. Oh, you want alerts.

##### **Chenyu** [[00:37:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2276)]
Basically what you are getting. No. Just find a channel. And that channel is fine.

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2284)]
OK. I like the message of the day. Yeah.

##### **Hooved** [[00:38:10](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2290)]
OK. Yeah.

##### **Geohot** [[00:38:15](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2295)]
Why? Why is H3 down right now? Yeah, reset. I mean, I wonder if we can get this on all the machines. Maybe not just the CI machines. Have like two graphs on stats.

##### **Chenyu** [[00:38:44](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2324)]
I think in general, it's pretty good. I think in general, let's get started with having the easiest way to know the status of the machine and how frequently are we rebooting those machines. That we can prioritize if we need to fix things.

##### **Geohot** [[00:38:57](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2337)]
Well, yeah. No. I want to do this for not just the CI machines.

##### **Chenyu** [[00:39:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2340)]
We should have every machine, including the dev machine.

##### **Geohot** [[00:39:03](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2343)]
Yes. Yes. Well, Speck, that easy?

##### **Wozeparrot** [[00:39:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2348)]
Yeah, it's fine. I just have to deploy the telemetry worker to everything else.

##### **Geohot** [[00:39:12](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2352)]
OK.

##### **Nimlgen** [[00:39:17](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2357)]
OK. OK. Next is symbolic.

##### **Sieds Lykles** [[00:39:22](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2362)]
Yeah. So I got D types index merged last week. And now the next thing to do is have the invalid index. And it's working on everything except rangeify. So just looking to that today.

##### **Geohot** [[00:39:40](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2380)]
Should be merged soon, hopefully. So we have a final.

##### **Geohot** [[00:39:52](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2392)]
There's a rewrite in the final pass that moves the back to the old stuff.

##### **Sieds Lykles** [[00:39:57](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2397)]
Yeah. OK, cool. I mean, before you do the D type lowering, before you move the D types index, it has to go. Oh, that makes sense. Yeah, yeah, yeah.

##### **Geohot** [[00:40:07](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2407)]
It should be at the same stage as the D type lowering. Yeah, just before that. But yeah.

##### **Hooved** [[00:40:14](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2414)]
So it should be at the same stage.

##### **Geohot** [[00:40:20](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2420)]
Yeah, maybe you want to actually explain it for the meeting?

##### **Geohot** [[00:40:23](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2423)]
I think index is exciting.

##### **Sieds Lykles** [[00:40:28](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2428)]
Yeah, so this idea is instead of

##### **Geohot** [[00:40:33](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2433)]
having like

##### **Sieds Lykles** [[00:40:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2437)]
whenever you have a mask or a pad or whatever, you have some indices that are invalid, and instead of creating a mask and then putting the mask on the index, we create the index with a where, and the where has a branch, and the false branch might be as a value called invalid, and invalid will never actually be selected.

##### **Geohot** [[00:41:05](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2465)]
Does it have to be the false branch? What if it's the true branch?

##### **Sieds Lykles** [[00:41:09](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2469)]
I make sure that it gets swapped to the false branch. It could be the true branch, but for the sake of all the patterns being the same, I swap it to the false branch. And then for the normal lowering that we have now, this actually is not that much different, but for rangeify it would be nice because then you can you're creating the padding or whatever before you you want to create the mask before you're actually on a buffer and then you want to propagate

##### **Geohot** [[00:41:55](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2515)]
this index until it hits a buffer or it can just

##### **Sieds Lykles** [[00:42:04](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2524)]
it changes the mask from being kind of more global to being very local on the index where it's created and then you could also imagine like removing a pad to optimization with switching out the range with a range that has invalid on it and then you just push invalid until it hits a

##### **Geohot** [[00:42:34](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2554)]
load or store and then yeah

##### **Geohot** [[00:42:39](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2559)]
the basic idea is there's this new dtype called dtype index. dtype index is a new dtype index that's actually called dtype index. dtype index is an unlimited precision integer and it also has a value called invalid. And if invalid is ever loaded from it loads a zero and if invalid is ever stored to it does nothing. So it's now just like a valid it's just like a an offset into the array. You can offset into the array invalid and when you offset invalid yeah your load from that zero if you store it away it's nothing so.

##### **Chenyu** [[00:43:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2588)]
Yeah my understanding of this is if you think about accessing certain entries of the array with an index that is only one. certain index of your buffer, you have a function from your so-called range, I guess, from your domain to your range. Then previously, what we do is we create a mask. We say if the mask is true, then it loads from the buffer. Otherwise, it loads zero. So this works on your output of indexing function. And this change will change that to your input of indexing function. So instead of saying we will have a different output, we say we have a different input. And the benefit of this is this index can then work on many of different buffers, and it can compose with another index and things like that.

##### **Sieds Lykles** [[00:43:58](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2638)]
Yeah. I mean, in the end, it still turns into a gate. You still end up pretty much with the same gated load and gated store we have now. When? Before? Before dtype index gets removed, because you can't actually have infinite precision integers on the GPU. But yeah, in this sort of intermediate stage, it's nice to have. It's a lot more flexible.

##### **Chenyu** [[00:44:28](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2668)]
Yeah, similar to, I think this is a very useful abstraction to have. Much better than lower everything to the smallest thing than try to. Like, compose loads.

##### **Geohot** [[00:44:45](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2685)]
Yeah.

##### **Chenyu** [[00:44:45](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2685)]
And with this, we can also do a lot of the wear fusion or load fusion before that was hard to do before. So excited about this.

##### **Geohot** [[00:44:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2696)]
Yeah, yeah, hopefully. So invalid is a const, right?

##### **Sieds Lykles** [[00:44:59](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2699)]
Yeah. Cool.

##### **Geohot** [[00:45:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2700)]
And it goes in vconst too?

##### **Sieds Lykles** [[00:45:04](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2704)]
Yeah, it goes into vconst, yeah.

##### **Geohot** [[00:45:06](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2706)]
Great.

##### **Hooved** [[00:45:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2708)]
Cool.

##### **Geohot** [[00:45:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2708)]
Exciting.

##### **Hooved** [[00:45:10](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2710)]
Hey.

##### **Chenyu** [[00:45:11](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2711)]
Oh, I'm excited. Cloud or I don't really know what's priority.

##### **Wozeparrot** [[00:45:16](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2716)]
Yeah, I'm not really glad I'll be this week.

##### **Chenyu** [[00:45:18](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2718)]
OK. We're going to get one. You got something done this week?

##### **Wozeparrot** [[00:45:23](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2723)]
But for this week, I'm mainly just removing two provisioning

##### **Geohot** [[00:45:28](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2728)]
machines and moving that to cloud.

##### **Geohot** [[00:45:37](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2737)]
Yeah, we got network cables are ordered. They should be here soon. And we now have the tiny room is very nicely insulated. We got the fans installed this weekend. So yeah, the tiny room is a real climate controlled zone now. I should put the sensors in before I leave.

##### **Sieds Lykles** [[00:45:57](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2757)]
Is it good? My air code is controlled by that room. It's better now, right?

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2762)]
Yeah. Yeah, right? Now that we.

##### **Sieds Lykles** [[00:46:03](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2763)]
It's not super cold.

##### **Geohot** [[00:46:05](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2765)]
It's not super cold because we isolated the computers. Yeah, we used to be burning. It was costing us like $2,000 a month to just build a room. Just running the overrunning the HVAC to Google computers. But now we're just putting a fan.

##### **Chenyu** [[00:46:20](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2780)]
Is it fine if we run all the BERT training on all the TinyBox in that room? Is it OK? Should be.

##### **Geohot** [[00:46:28](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2788)]
Should be. Yeah, yeah. Actually, if you want to stress this, now's a good time. No, I don't know.

##### **Chenyu** [[00:46:36](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2796)]
I feel it should be done by someone who is literally there. OK. Yeah, yeah. Yeah, I see. Yeah, yeah, yeah. OK, anyway. Cool. Cool. OK, other bounties.

##### **Geohot** [[00:46:51](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2811)]
Let's start with training.

##### **Hooved** [[00:46:59](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2819)]
So I don't have much to say beyond what I wrote. I should know later today if it converged or not, my most recent run. I'm running it in float 32. Yeah. with matching the MLPerf batch size and learning rate. So just to try to have as low room for error as possible. And then if that works, I'll back off and use BF16.

##### **Geohot** [[00:47:28](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2848)]
Is there a chance we can get this submitted for MLPerf? Because I'd really like to get one thing submitted.

##### **Hooved** [[00:47:32](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2852)]
No, because we discussed this back when I started the bounty.

##### **Chenyu** [[00:47:40](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2860)]
Change the target this time.

##### **Geohot** [[00:47:46](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2866)]
Also, you shouldn't be, if you're having a hardware issue with the computers, just if you're confident there are hardware issues, we got to fix that. We shouldn't be giving you broken computers.

##### **Hooved** [[00:47:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2876)]
Thanks, I appreciate that. I mean, it's actually pretty stable now, now that I've learned how to power limit it and so forth. But maybe we can make it better so I don't have to power limit it as much.

##### **Geohot** [[00:48:05](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2885)]
You're on TinyAMD 1? Yeah. I'm on 2x3. And it's only GPU 3 that ever has issues, right?

##### **Hooved** [[00:48:12](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2892)]
No, there was that one time GPU 1 caused the crash.

##### **Geohot** [[00:48:18](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2898)]
Oh. But the power limiting thing is only 3?

##### **Hooved** [[00:48:23](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2903)]
No, I haven't really had much issues. I'd have to go back and look through all my comments. But I think even when it was power limited, I had issues on GPU 1. But like the weird thing is, I don't know if it's fixed by power limiting, it's only GPU 3. So it's like different issues, different GPUs.

##### **Geohot** [[00:48:45](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2925)]
I see. Well, what I can do is swap GPUs with AMD 2. That's pretty much what I can offer.

##### **Hooved** [[00:48:51](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2931)]
And we're sure that those don't have issues that are causing them?

##### **Geohot** [[00:48:55](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2935)]
I'm just saying what I can offer. I have no idea what has issues and what doesn't have issues. But I have the machines 100 meters from my office.

##### **Hooved** [[00:49:03](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2943)]
All right. Thanks. I'll let you know. I'll follow up on that.

##### **Geohot** [[00:49:07](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2947)]
Cool.

##### **Hooved** [[00:49:09](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2949)]
OK.

##### **Chenyu** [[00:49:15](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2955)]
How's the status of merge, assign, and store you up?

##### **Geohot** [[00:49:19](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2959)]
Yeah. I'm happy to pay out that bounty. It's kind of, I don't want to mess with this until after rangeify is merged. But yeah, it was $200. I should pay Cordis out the bounty. But I'm not sure if I'm going to merge that. I'm going to pay Cordis out right now.

##### **Hooved** [[00:49:39](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2979)]
OK.

##### **Geohot** [[00:49:40](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2980)]
We merged part of it. We merged the less controversial parts of it. The part that's still left, there's not anything really wrong with it. It's just like, I don't know how it plays with rangeify. So.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2994)]
But yeah, I'll pay that bounty out.

##### **Hooved** [[00:49:56](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=2996)]
OK.

##### **Chenyu** [[00:50:00](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3000)]
Whisper Web GPU, we will have a demo soon.

##### **Hooved** [[00:50:05](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3005)]
OK.

##### **Geohot** [[00:50:08](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3008)]
What else?

##### **Geohot** [[00:50:10](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3010)]
What else? I put up an $800 bounty for Winograd as a rewrite rule.

##### **Hooved** [[00:50:20](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3020)]
OK.

##### **Geohot** [[00:50:25](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3025)]
It should be doable, like after the Rangification. So like after the lower. If you detect these overlapping ranges, you should be able to just apply the Winograd patterns to them.

##### **Chenyu** [[00:50:36](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3036)]
Well, there's another thing that I'm going to do. But I tried a few times. So I think now our conf has two implementation. And it should be one. And ideally, the backend should simplify all those.

##### **Geohot** [[00:50:54](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3054)]
Oh, wait. Do you mean the thing in pool where it has that if statement? Where I say if the ShapeTracker is better? Yes.

##### **Chenyu** [[00:51:02](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3062)]
So now we are deleting ShapeTracker.

##### **Geohot** [[00:51:06](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3066)]
Oh, yeah. So to do. Once the ShapeTracker can optimize well, remove this alternative implementation. Yeah. On rangeify, that's going to be the same, I'm sure. Yeah.

##### **Geohot** [[00:51:16](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3076)]
So that's something I'm excited about.

##### **Geohot** [[00:51:22](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3082)]
OK. Actually, only the alternative implementation uses pad.

##### **Geohot** [[00:51:32](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3092)]
Interesting. Well, that's because you have stride, right? So you need to make it a multiple of stride. Yeah. Oh, which one can I remove? Oh, I can remove the one in the if statement. I think we want to remove the one out of the if statement.

##### **Geohot** [[00:51:58](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3118)]
That's the one that has pad. I don't know. But either way, yeah, let's get after rangeify is merged, I'm sure that this won't be a problem anymore. Great. Or whatever it is, we'll have to make sure Symbala can do it. But yeah.

##### **Chenyu** [[00:52:11](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3131)]
Yeah, I think if you try to do it now, there are some issues with the multi-view and generating some garbage kernel.

##### **Geohot** [[00:52:20](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3140)]
Yeah, I believe that. ShapeTracker. I wrote that thing up on Twitter. Hopefully it's like, ShapeTracker is just wrong because if imagine three views on a ShapeTracker, you want to slice them vertically. Yeah. Shape trackers didn't have good stuff for this.

##### **Geohot** [[00:52:39](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3159)]
You see what I mean by slice them vertically? Real stride.

##### **Geohot** [[00:52:45](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3165)]
Well, not even real stride, but like, if you have like a seven dimension tensor and all you're doing is permuting the last two dimensions, like the other five are just staying still. And ShapeTracker doesn't express this through multi-view at all. Like you want to slice this thing vertically.

##### **Chenyu** [[00:53:02](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3182)]
It's real stride and you will have the same number for your real stride.

##### **Hooved** [[00:53:06](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3186)]
So that's a little bit of a.

##### **Geohot** [[00:53:11](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3191)]
Yeah, I mean, kind of.

##### **Geohot** [[00:53:12](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3192)]
Look at what real stride is. Like, yeah, real stride is basically range-file. Sure. Yes. Yes. Sure.

##### **Hooved** [[00:53:19](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3199)]
Great.

##### **Chenyu** [[00:53:21](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3201)]
Anyway, now the stride part is factored into range-file. Everything should be good. And we can remove a lot of weird, who knows if there are bug merge logics.

##### **Geohot** [[00:53:35](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3215)]
Yeah. Yeah. Deleting that merge view logic. That was code in tinygrad I could not read. That was the only thing in tinygrad I couldn't read.

##### **Geohot** [[00:53:43](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3223)]
I still can't read it. I think the logic is quite straightforward. The problem is we know it's limited. What? Reshape mask? Yeah. You can read this? Oh, sure. Why not? Yeah.

##### **Chenyu** [[00:54:05](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3245)]
OK. It's better than it used to be, but still. Yeah. I mean, the main problem is not readability for me. It's mostly there are things I know should be done, but we just don't know how to do it. Hopefully that's gone and not a problem in the future. So that's it.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3261)]
Yeah. I see. Yeah, that was always a piece of code I can never understand. Oh, now it calls that simplify. OK. It actually is better than it used to be.

##### **Chenyu** [[00:54:31](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3271)]
Yeah, now it's just a bunch of simplify. And I think it's fine. I think really the core thing is real stride. And once we remove that, that would be nice.

##### **Geohot** [[00:54:40](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3280)]
Yeah. So real stride's already only used. It's only used right now for the reduce split, which should also be a rewrite rule that's later.

##### **Chenyu** [[00:54:52](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3292)]
Yeah. And there's an input argument goes into a function, the ignore valid. I made a quick attempt to remove that. I don't know if it's worth doing, given that we are going to remove it altogether. I mean, yeah.

##### **Geohot** [[00:55:07](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3307)]
So right now there's no way to do that reduce split lower level, because the range of vacation is still happening at the kernel level. So you can't split the reduce. You have to still split it in the big graph world. But yeah, after a range of five, we can just split it. We can make that a rule that just uses the range stuff. And it should be a lot simpler. And then we can delete real strides. Range of five cost function this week. Great. Sounds good.

##### **Chenyu** [[00:55:36](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3336)]
OK.

##### **Geohot** [[00:55:38](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3338)]
The other exciting stuff. Bunch of people on Twitter using tiny graph, which is good.

##### **Geohot** [[00:55:50](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3350)]
Wait, what are they use this for? All kinds of various. Like they're not like major things, but they're just like people are like, oh, this is like. I can actually write stuff and understand what it's doing.

##### **Chenyu** [[00:56:06](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3366)]
So I can just do it. I like the project that do the forward only training, something like that.

##### **Geohot** [[00:56:13](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3373)]
Yeah.

##### **Hooved** [[00:56:17](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3377)]
OK.

##### **Geohot** [[00:56:19](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3379)]
Sounds good.

##### **Chenyu** [[00:56:22](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3382)]
I think that's about it for this meeting. Next week, same time. See you. Bye. Bye.

##### **Hooved** [[00:56:31](https://www.youtube.com/watch?v=5-0CYqlEE2c&t=3391)]
Bye. Bye.
