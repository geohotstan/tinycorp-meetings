# 2025-04-28 Meeting

### Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time)
- company update
- new arange reduce fuser
- bert, mlperf, retinanet
- scheduler
- driver
- tensor cores
- webgpu
- unrolled arange div
- cpu graph / llvm graph
- sdxl speed
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=9_7IhCYt1Kw)

### Highlights

- **[Company Update](#geohot-000010)**: TinyBox Green V2s are shipping soon, with tracking numbers in hand. Price raised to $29,000 due to increased costs; estimated delivery in 2–8 weeks.
- **[New Arange Reduce Fuser](#geohot-000136)**: A new, more general rewrite rule simplifies Arange reductions by pushing out add/mul operations, making the system more robust and extensible.
- **[MLPerf BERT Progress](#chenyu-000454)**: Green and MI300X runs completed; Red runs pending. Final submission targeted before Chenyu’s flight; driver issues causing NaNs identified as AMD-specific.
- **[RetinaNet MLPerf Status](#flata-000754)**: Most runs successful after hyperparameter tuning; optimizations reduced tensor transfer time significantly by reassembling tensors on GPU.
- **[Scheduler Updates](#qazalin-001233)**: Multi-output scheduler refactor nearing merge. Discussions on bugs in FuseKernelSoftmax and binding variables in schedules; bug fixes prioritized over new features.
- **[Emulator Investigations](#geohot-001300)**: Exploring using an existing RDNA3 emulator rather than maintaining a custom one; potential benefits discussed.
- **[Driver Work and USB GPU](#nimlgen-002324)**: USB GPU support progressing; goal to merge soon, followed by speed optimizations. PSP bypass explored as a potential major speed improvement.
- **[TensorCore Validation Issues](#ignaciosica-002943)**: Two bugs identified—one from TinyGrad validation assumptions and one possibly from ROCm compiler optimizations (O1 vs O2); plan to isolate and report to AMD.
- **[WebGPU Graph Work](#hooved-003415)**: WebGPU graph being split for easier merging; broader discussion emphasizing correctness over speed and encouraging usability improvements over complexity.
- **[Unrolled Arange Div Simplification](#geohot-004458)**: Unroll Arange division logic improved with Z3 constraint solving support; new PR looks clean and near merge-ready.
- **[CPU Graph/LLVM Graph Bounties](#geohot-004544)**: LLVM graph integration work is progressing; bounty likely to be awarded if PRs merge successfully.
- **[SDXL Speed Improvements](#geohot-004752)**: Stable Diffusion times are about 18% slower than PyTorch non-flash attention variant; single-kernel optimizations ongoing to close the gap.
- **[Other Bounties and FP8 Discussion](#geohot-004912)**: FP8 support PR criticized for poor code quality; plans to rethink the design to avoid scattered complexity and possibly align with BF16 handling standards.
- **[Linearizer and Reduce Bugs](#geohot-005416)**: Linearizer issues from unparented reduces addressed; better structured code reduces need for hacks and fixes subtle symbolic bugs.
- **[Z3 Dependency Discussion](#geohot-005742)**: Decision to not make Z3 a core dependency unless absolutely necessary; current needs don’t justify it.
- **[Meeting Time Adjustment](#chenyu-010000)**: Meeting will move two hours later to better accommodate California-based contributors; next week's meeting at 9AM PDT.


### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=0)]
Let's get started.
Start with company update.
I heard 5090s are here.

##### **Geohot** [[00:00:10](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=10)]
5090s are not here yet, but they've shipped.
We have a tracking number.
So yeah, we're going to get out.
There's three fully paid TinyBox Green V2s.
They should ship in, let's say, two to eight weeks, depending on other suppliers.
And then we've upped the price to $29,000.
I don't think the price is going to go back down.
I mean, everything just costs us like 20% more.
So we're passing that lack of savings on to you.
uh i saw the the clone competitor people were quoting 31,000 for a for 5090 bucks so we're price competitive this is where it's going to stay for the generation uh yeah and if you order one today yeah it'll ship in uh two to eight weeks

##### **Chenyu** [[00:01:20](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=80)]
Great!
Anything else?

##### **Geohot** [[00:01:24](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=80)]
Nope.

##### **Chenyu** [[00:01:30](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=90)]
You want to talk about a new reduced fuser, the rewrite for Arange thing?

##### **Geohot** [[00:01:36](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=90)]
Yeah, so I wrote a rewrite rule.
The new one's even better.
The one that's pending the unroll div thing is even better.
It doesn't...
It doesn't match a rule and remove the Arange all at once.
It does some transformations to simplify it, and then things can be really, really simple.
With adds and muls and stuff.
We used to have code to deal with hand-coded add chain stuff, and it was dumb.
What you really want to do is pull as much out of the reduce closure as possible, and then if your reduce closure becomes a very limited set of patterns, you can remove the reduce.
So that's what the new one does.
It's a little bit slower, but it works for a ton more cases.
It should never not work.
And if there's a case where Arange isn't folding, it's pretty easy to add a rule now.
Whereas back in the day, if Arange wasn't fusing, you'd have to like, it was like an exponential explosion.
You'd have to add every combination of add and mul every order of them.
And now you can just push the adds and the muls out of the reduce.
So that's what it does.

##### **Chenyu** [[00:02:52](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=167)]
Is it also simple to add max?

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=167)]
Yep.
Yep.
It might already work for max.
If it doesn't work for max, it's like a one-line change.

##### **Chenyu** [[00:03:04](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=180)]
OK.
I can take a look.
Yeah, I try something, try a lot of stuff.
I have a list of things to try.
Uh, I think max didn't work.
And if you want to be really crazy, you can do arange and tensor indexing another arange.

##### **Geohot** [[00:03:26](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=206)]
Yeah.
So we should get the, we should get that PR, uh, like we should get that PR emerged.
That changes it to use the, like, it doesn't change the range anymore.
Changing the range is kind of bad.
It just pushes things out of the reduce.
And then once that's merged, that's a really good thing to work on top of.
So yeah, all those things should be like one line fixes.
Great.

##### **Chenyu** [[00:03:49](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=206)]
I imagine in contract, that's the change the ranges back to only be the count.

##### **Geohot** [[00:03:55](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=206)]
So yeah, I got rid of the three-term ranges.
But I actually think we should move all ranges to be one-term ranges.
But that's a decently big change across the code base.
There's no reason that a range should have two terms.
Because if you have a range from s to e, you can always express that as a range from 0 to e minus s, where the 0 is implicit, and then just plus s.
Just to create a way to express it.
And then eventually, what we want to do with ranges is the range should be rewritten into the for loop.
The range should be rewritten basically as an accumulator.
And the index of the range, the variable in the range should become an accumulator.
And then we can do all sorts of new tricks with indexing.

##### **Chenyu** [[00:04:54](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=294)]
Sounds good.
Cool.
Okay.
Yeah, we can talk about the unroll arrangement later.
Moving on to MLPerf.
I posted in the BERT channel.
We got the green runs and the MI300 runs relatively smoothly.
That was nice.
Red runs should be ready by the end of
And today, I think, I need more hours.
So yeah, end of today.
And that concludes BERT and should be ready to make a submission tomorrow.
I want to do that before my flight.
Our final time looks like, I'll post the final time once we're there.
I think we are 110 minutes for MI300X, 210 for greens, and 800 for reds.
So at the end, our red can only be wrong with AMD driver because of the NAN issue.
I'm pretty sure it's AM issue because once I switched to running with AMD, it no longer happened.
That's slightly slower.
It's like 5% slower.

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=294)]
Yeah.
I mean, I totally believe, if that's what you saw, that it's the driver.
And it makes me wonder how many people have NAN issues in their big training runs that are actually caused by.
bad runtimes or drivers.

##### **Chenyu** [[00:06:30](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=294)]
Yeah.
So I know the tricks people use is something like you can add before your true gradient updates.
It depends on where this NAN happens.
If it's randomly what happens, then there's no help.
But otherwise, numerical issue, if it's known to be numerical issues, then we have ways to bypass the bad batch or something like that.

##### **Geohot** [[00:06:56](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=294)]
Well, yeah, but if it's the driver, the fact that AM and AMD should be running the exact same thing, right?

##### **Chenyu** [[00:07:03](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=423)]
Yeah, and especially because we also set up with AM, so there's no way we are saying it generates a different code.
So that's something.
I will have a write-up on this for all the things we know that should be improved and things that
the bugs that we discover and other stuff.
After I make a submission, I will have a write-up ready.

##### **Geohot** [[00:07:29](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=449)]
Great.
Yeah, we should put a blog together.
We should have a TinyGrad blog.
It would be cool to write it up.

##### **Chenyu** [[00:07:40](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=457)]
I'll write it and put it somewhere in the repo, and if people are interested in making a blog, sure.
Yeah, and we got retinanet,
Great.

##### **Flata** [[00:07:54](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=474)]
Uh, yeah, I, yeah, so that was, that took quite a bit, but, um, overall, everything looks good.
I think out of all the five runs, just one didn't converge, but, uh, the H param changes that Chen you made, uh, is actually more consistent than the one that I initially introduced.
So, yeah, I think now I'm just focused on rewriting the post-processing step into tinygrad and hopefully we can get some good speed ups and then we can go from there.

##### **Geohot** [[00:08:19](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=499)]
Which, uh, which computer?

##### **Flata** [[00:08:22](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=499)]
Uh, the tiny box screen.

##### **Geohot** [[00:08:24](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=499)]
Green, OK.

##### **Chenyu** [[00:08:26](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=506)]
So this is great.
We will submit it.
There are several issues with red.
One is very likely we are hitting the Tensor Core padding bug, whether it's in TinyGrad or it's in the compiler.
I think compiler definitely contribute to some of it.
Maybe we have some bugs in TinyGrad.
I don't know.
But because of that, we cannot even run with AMD runtime or the same tricks to the BERT, because the generative kernel is likely to be wrong.
Does it happen with AMD LLVM also?
I didn't have time to try, but we can try it after we have the script merging back to master.

##### **Geohot** [[00:09:14](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=554)]
Yeah, no, I think it's just worth trying.
Just run it with AMD LLVM and see if it still works.

##### **Chenyu** [[00:09:19](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=559)]
So I think the repro I gave, the one that we false tensor core, that also failed with AMD LLVM.
And I believe running AM on this also hits the weird non-issue, because you can generate values that's very wrong.
So if it's a numerical issue, then you know when you compute accuracy, you either get a real number between 0 and 1, or you get NAN. But we have seen negative 10 to the power of 500 or something like that.

##### **Geohot** [[00:09:57](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=597)]
Oh, that's interesting if we have a simple AM failing repro, like a simple place where AM and AMD diverge, because they shouldn't diverge.

##### **Chenyu** [[00:10:06](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=606)]
Yeah, so I think that's part of the short term to do is that we like to be fixed.
But anyway, we have retinanet.
I think the final time is I made a big...
All the slowness is coming from we copied a very big tensor for eval from
from GPU to CPU, and for the numpy process on that big CPU tensor, it's also slow.
I called it slow, so I think the only tricks I did to make it faster was moving the... 
For now, when we reassemble multi-tensor into one, that's default down on CPU, and if it's really big, it's very slow.
So I move that to gpu0, and that saves like two hours.

##### **Geohot** [[00:10:56](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=606)]
Wow.

##### **Chenyu** [[00:10:57](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=657)]
Yeah, that copy is very slow.
I didn't realize copying from host to device is 6 gig per second, but the reverse is like 1 gig per second.
I don't know if it's like pin memory or we can do something special.

##### **Geohot** [[00:11:15](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=675)]
I mean, when you're copying for device to host, it's even less of an excuse for not having pin memory.

##### **Chenyu** [[00:11:22](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=686)]
Yeah.
OK, anyway, we don't have that now.
So our time is like 14 hours.
We are, I think, eight hours for training and six hours for eval.
We'll probably put a line somewhere in the to reviewers saying, no, that's a split, and we didn't really optimize for that.

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=705)]
Yeah, no, I think it's just great to have a time on the board.
We can do better next time.

##### **Chenyu** [[00:11:50](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=710)]
I think for the bounty, we probably, I think the difference between this one and previous BERT, which was also not a great time, is this time we didn't do green, we didn't do red, and there's obvious flaw in the eval.
So I think I'm still interested in $1,000 bounties to make it good.
I think we just target something like 8 hours with our obvious bad thing next time.

##### **Geohot** [[00:12:16](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=736)]
Sounds good.

##### **Chenyu** [[00:12:19](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=739)]
That's MLPerf.
I will make a submission tomorrow.
Very good.
Then I will follow up with whatever review.
I think the final review will be out in a month.
With that, we can move on to scheduler.

##### **Qazalin** [[00:12:33](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=753)]
I actually worked a bit more on the emulator this week, but now I'm back on the scheduler.
since today, and I think I'm going to merge multi-output very soon, early this week.
So far, there are already enough refactors and infrastructure merging to master that multi-output is an easy new graph-free write-pass.
I think I have to make it a new graph-free write-pass.
It's hard to reason about it.

##### **Geohot** [[00:13:13](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=788)]
Well, let's take a minute and first talk about the emulator stuff.
So I think it really is worth it to get that other emulator running.
Any... You look at that at all?

##### **Qazalin** [[00:13:32](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=788)]
I didn't try to hook it up to TinyGrad.
I just ran examples on it.

##### **Geohot** [[00:13:36](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=788)]
I mean, it does seem to work.
We should not be maintaining an emulator if we don't have to.

##### **Qazalin** [[00:14:00](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=840)]
I think the reason why it took me so long was because I read the documentation wrong.
Maybe the docs were wrong.
I don't know.
But yeah, I'll look into that.
I'll look into the emulator.
I honestly, like, if we can move on to something that's bug-free, I'll move it.
It looks like an abandoned project, though.
Like, it's not in any updates for three years, right?

##### **Geohot** [[00:14:25](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=865)]
Well, it does look like an abandoned project.
But no, I'm saying if their baseline plays... I mean, it's also a speed question, right?
We could quickly benchmark their emulator against Remu.
And if it turns out to have bugs and be slower, then okay, forget about it.
But if it turns out to not have bugs and be faster, then we might want to switch.
You always have to avoid sunk cost fallacies with things.
You always just have to say, if this one turns out to be better, I wish we'd spent more time in the beginning looking around to see what we could find.
How shocking is it that there's a whole RDNA3 emulator that just exists?
The other advantage to that emulator is that it's a simulator.
It's an actual emulator.
It can actually emulate the cache.
It can emulate everything.
Again, I feel like you could spend two hours on it and be like, wait a second, this is actually super crappy for all these reasons.
So I don't know how good it is.
But yeah, I think there's value in the full stack there.
I'm also interested, and now that you spent time doing the hardware thing too, if there's really a kernel that's running differently on AM and AMD, like reliably runs differently, let's trace it to the hardware and figure out exactly what's going on.
That's like a super valuable failing test.
But yeah, that's all I got on that.

##### **Qazalin** [[00:16:30](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=990)]
OK, yeah.
I'll go into scheduler work, because I know that we have multi-output.
And I also want to do, after multi-output, fuse arange default.
I know there's bugs with padding that makes llama fuse arange not work.
The problem is basically that if you have two Aranges on different dimensions, you can't put them in one kernel.
Or if you can, you have to pad one Arange.
It's a little tricky because it's not local.

##### **Geohot** [[00:17:01](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1021)]
I see.
So that's the failure.

##### **Qazalin** [[00:17:07](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1027)]
You basically have two Aranges.
One has an N of 13.
The other one has an N8.

##### **Geohot** [[00:17:14](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1034)]
And they're on the same axis.

##### **Qazalin** [[00:17:18](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1038)]
They're on the same axis.

##### **Geohot** [[00:17:21](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1041)]
Interesting.
Yeah, I also posted two scheduler issues in the scheduler channel.
So there's an infinite loop with that single kernel softmax.
And then there's the issue where, what do you do if a variable is bound to two different things in the same schedule?

##### **Qazalin** [[00:17:42](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1062)]
I think my first instinct would be to assert that. That should never happen.

##### **Chenyu** [[00:17:56](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1076)]
We probably currently assert that, no?

##### **Geohot** [[00:18:00](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1076)]
We do not.

##### **Chenyu** [[00:18:02](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1076)]
There's a merge dict helper that's specifically for asserting that.

##### **Geohot** [[00:18:08](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1088)]
Well, whatever happened, I wrote this, it clearly... Yeah, so I think there's two acceptable things to do here.
One is to make it work as intended, or the other is to assert.
The current behavior is it just takes the second bind and just uses that one.
So that's just wrong.

##### **Qazalin** [[00:18:30](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1110)]
I see.
I'm not using merge dicts.
I'm using an update on the Python dictionary.
That's an easy one.

##### **Chenyu** [[00:18:38](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1118)]
If you update to use merge dict, I think we at least assert, then we can decide if we want to change the behavior.

##### **Qazalin** [[00:18:45](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1125)]
Yeah.
There's also the issue with the mental on the buffer count limit.
So in the SDXL, I think you posted that.

##### **Geohot** [[00:19:00](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1140)]
Oh, yeah, but that's not an actual buffer count limit issue.
That issue has nothing to do with metal in the buffer counts.
There's a bug.
There's actually a deep scheduler bug somewhere.
I also posted, if you run all of the stuff with Fuse Kernel Softmax, I think this is why BERT got slower.
I think there's some scheduler bug with Fuse Kernel Softmax.
Because you can look at what's happening.
If you use, like, set GPU=1 and do that, you'll see that the linears start to have 100 inputs.
So yeah, that's a bug.
That's not the actual metal thing.
The metal thing is just helping us find that bug.

##### **Qazalin** [[00:19:38](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1178)]
See, yeah, it should definitely do that.

##### **Geohot** [[00:19:41](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1181)]
Yeah, I'm much more excited about these things being fixed than multi output.
Yeah, bug fixes first, and then...
That's good.

##### **Chenyu** [[00:19:55](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1195)]
Yeah, I will add more.
I think I read from a few, but I will actually make some test Arange or the fusion test in unit tests or somewhere.

##### **Geohot** [[00:20:07](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1207)]
Yeah, just tracking down exactly what it is that's causing this blow up would be interesting, that's causing this kernel blow up.
Yeah.
because single kernel softmax should also get us single kernel softmax and single kernel layer norm should also i think get us faster stable diffusion than torch without flash tension.
yeah i was playing with the yeah there's a few kernels not in the JIT that will help but it's not that bad

##### **Chenyu** [[00:20:47](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1247)]
I don't know.
There are some weird math stuff, even from the original stable diffusion repo, that things can be simplified mathematically, but not as a rewrite rule that we can apply.
It can also make it slightly faster.

##### **Geohot** [[00:21:04](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1264)]
I mean, our time is not that bad.
We're only 18% slower than the non-flash attention variant of Torch.

##### **Chenyu** [[00:21:13](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1273)]
Yeah, but they will also say, oh, you should use Torch compile on this thing, right?

##### **Geohot** [[00:21:18](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1278)]
No, no, no, no, no.
So we're 77% off the best thing that they've ever gotten.

##### **Chenyu** [[00:21:25](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1285)]
Is that using Torch Compile?

##### **Geohot** [[00:21:26](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1288)]
I'm sure.
I think it's all using Torch Compile.
With Flash Attention, we're not that far off.
So we're getting...
Yeah, I don't know.
Feeb is doing something.
I don't know what he's doing to get times that are really bad.
I think there's some bug in his setup.
But we're only, without Flash attention, with their best variant they've ever seen, we're less than 2x off.

##### **Chenyu** [[00:21:57](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1317)]
Great.
Let's make it fast.

##### **Geohot** [[00:22:01](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1321)]
Yeah.

##### **Chenyu** [[00:22:02](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1321)]
Yeah.
I think this is also tied to a speedup default or something something project.
Eventually, we want to run the Beam version of this CI benchmark.

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1337)]
Yeah.
Yeah.
No, we definitely don't have any Beam CI.
We have Beam CIs for LLMs.
We don't have any Beam CIs for any conv-y stuff.

##### **Chenyu** [[00:22:25](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1345)]
We have one conv let's being beam.

##### **Geohot** [[00:22:28](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1348)]
Well, yeah, the one conf in the conv speed test...
It's also not in the chart!

##### **Chenyu** [[00:22:37](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1357)]
Chart is an issue that our upcoming intern will fix the dashboard.

##### **Geohot** [[00:22:44](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1364)]
Yes, yes, true.

##### **Chenyu** [[00:22:46](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1364)]
Give us an API, and we can update the dashboard.
Cool.
Yeah, I don't know.
I can try to reproduce this.
If George and I produce the same speed, it must be some setup issue, right?

##### **Chenyu** [[00:23:08](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1388)]
Okay, that sounds good.
Yeah, let's move on to driver.
Yeah.

##### **Nimlgen** [[00:23:24](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1404)]
So yeah, for the NAN issue, I'll take a look into that.
Actually, I've got one kernel where AM and AMD show different numbers.
But AM results are correct in this case.
And I don't understand now why AMD shows different results.
And it's not page fault.
It's pretty simple kernel.
But yeah, at least we have this difference.
So yeah.
So yeah, I'll investigate this.

##### **SPEAKER_04** [[00:24:07](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1447)]
so for so yeah also we now have fuzzer so it's been running on tiny32 from time to time so at least it already found one bug with AM so yeah
But still, it's not related to the NAN issue.
But OK.
So for the USB GPU, so if it sounds good, I would like to stop iterating on this speed and get everything merging tomorrow or in two days.
Yeah, and iterate on top of the master later.

##### **Geohot** [[00:24:53](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1493)]
Yeah, so I'll be back.
be back in san diego at the end of the week uh and i'll have access to all the hardware uh and i'll set something up in ci that can uh that has a has a gpu usb and we can just start measuring the speed and ci um yeah how much of that that 60 second call boots pretty bad how much you think that's going to come down?

##### **Nimlgen** [[00:25:25](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1525)]
Yeah, actually, we need a lot of firmware to load.
Like, we need all this RLC stuff to load SDMA, SMU, AMU.
So, yeah.
I don't know.
Like, the only what I can try to do is, during my refactor, is just try to fuse more writes.
So, I mean, that should be faster.

##### **Geohot** [[00:26:01](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1549)]
But first step is to get into master, and then let's drive that speed down.
But yeah, no, I'm obviously also interested if there's a PSP bypass.
That should just get us everything free.

##### **Nimlgen** [[00:26:17](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1577)]
Right, yeah.
Actually, I have to delay Mac.
So yeah, the PSP is the biggest blob.
Like this size over here.

##### **Geohot** [[00:26:32](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1592)]
I mean, the PSP bypass would be even better.
I think it's worth putting... First step is getting this merged into master.
Before you put a ton of time into optimizing the speed and the firmware order, spend a day seeing if there's some way to just not use the PSP, which is great for many reasons.
And then, if that works, you don't even need SDMA.
You can just write your own
10-line GPU kernel that does a memcopy.
But not a kernel, the GPU firmware.

##### **Nimlgen** [[00:27:07](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1627)]
Yeah.
But yeah, I think actually the USB latency is pretty big, even on the NVIDIA drives.
So the typical SDMA, even after the firmware booted, it also takes some time.
So actually,
like the copy into the controller is it's pretty fast but there is some latency as well so i mean it's just 0.4 milliseconds like to copy four kilobytes so and that's give us like 12 megabytes a second so and that's actually because of the usb latency like and it's the same on the nvme but in on nvme we can send like
bigger sizes than 4k because like it's it has internal processing on this controller like to feed the nvme but we should do like the round trip to the cpu so yeah 

##### **Geohot** [[00:28:15](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1627)]
i see uh yeah again yeah i think we can i think we can worry about this later uh i'm not that worried about 12 megabytes 12 megabytes a second is is like really fine

##### **Nimlgen** [[00:28:31](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1711)]
Yeah, OK, so yeah.
Yeah, I'm going to merge this into master.
Yeah, clean it up.
And we'll iterate on speed later.
And I mean, after that.

##### **Geohot** [[00:28:44](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1724)]
Yeah, and I mean, a PSP bypass would be lovely, too.
It should be so nice to just not run the PSP in any of these things.
I spent a couple hours looking into,
If we could figure out how to use AMD EPYC CPUs that are the locked ones, the locked ones are so cheap.
The locked chips are 5x cheaper than the unlocked chips.
They're just locked to Dell computers.
But a totally different thing.
But yeah, PSP bypasses are cool.
Yeah, okay.

##### **Chenyu** [[00:29:28](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1755)]
That's good.
Let's move on to TensorCores.

##### **Ignaciosica** [[00:29:43](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1783)]
Hi. Hello.
Last week I've been taking a look into the AMD Tensor Core bug.
I think there are two distinct bugs.
The one that is, both are hitting on the fuse matmul reproduction, but all the error, the bugs that appear on the completion site can be suppressed by changing the flag to a one.
But there's still a bug that it's from TinyGrad itself.
It came down to how the validation is done.
The validation expression is generated and the index expression.
It's a very special case where
It doesn't affect correctness in the general sense, but it does because the tensor cores expects a very specific thread pattern.
So that's why it's wrong.
The problem is that it's indexing, it's validating the expression with an
with an index that it has strike zero, so it doesn't appear in the index expression that is valid.

##### **Geohot** [[00:31:05](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1865)]
Well, let's let's stay on the on the compiler bug.
Can you write up what the compiler bugs are?
Can you make a test such that you can show provably different behavior with 01 and 02?

##### **Ignaciosica** [[00:31:17](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1877)]
OK, yes.

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1881)]
Yeah, like.
Find minimal tests where O1 and O2 disagree.
Make sure you're on the latest ROCm, and then let's report those to AMD.
Yeah, because like, it's so annoying if the thing that we're targeting actually is a broken compiler.
Like you can say, oh, I can change it to O1 that's fine.
But I mean, that's not a solution we could possibly do in production.
Like we need a compiler that's reliable.
So yeah, no, I think I think our write up of that is super valuable.
Just saying like, like, especially the smaller you can make the write up the better.
I remember some of the old compiler bugs had to do with register spelling.
But if there's stuff that's not register spelling, if there's stuff that's straight up wrong compiler transformations, that's super valuable to AMD.

##### **Ignaciosica** [[00:32:14](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1934)]
OK.

##### **Geohot** [[00:32:16](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1936)]
For the other bug with the zero strides, for other bugs in Tensor Cores, I kind of think we just want to move to the other way of doing Tensor Cores.
The current way of doing Tensor Cores is kind of never going to be good because you have this TC op, and the TC op relies on things being in a special order upstream.
And this is a pretty, like, it's not a reliable way to do this.
But what we should do is we should move the lidx to be vectorized.
With vectorized lidx, we can make the tensor cores work.
I guess with rewrite rules.
Do you remember that?

##### **Ignaciosica** [[00:33:01](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1981)]
I mean, it's what you told back then about pushing
pushing back, right?

##### **Geohot** [[00:33:11](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=1991)]
Well, would that fix these bugs?
Would your stride bugs just kind of go away and not be a thing if the LIDX, so not the GIDX, the GIDX is actually Dtype int, but the LIDX under the hood is the full Dtype, is the size of the warp.
Would that fix it?

##### **Ignaciosica** [[00:33:40](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2020)]
I don't think so.
This bug is, I don't know, it's very specific in the sense that.

##### **Geohot** [[00:33:53](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2033)]
OK, let's start with the compiler right now.
Yeah, yeah.

##### **Chenyu** [[00:34:04](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2033)]
Cool.
WebGPU?

##### **Hooved** [[00:34:15](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2055)]
I'm working on a PR to get the WebGPU graph broken out of the other stuff and see if we can merge that.
As part of that, I think I spotted potential more speed gains that won't come with much complexity.
In terms of, at least for Llama, for example, most of the command queue doesn't change.
It's not dependent on symbolic variables.
But it's currently all being computed dynamically.
So that's one thing that could be improved even without the graph.
So that might be separate PR if it works out.
So yeah.

##### **Geohot** [[00:34:59](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2099)]
Well, let's talk about that.
So what I'd imagine you're proposing is something that's going to split the command queue into multiple chunks, depending on whether it's symbolic or not.
So the problem with doing that is you're adding complexity, right?
It's not worth it.
Every single time when you're thinking, I'm going to add complexity in exchange for speed, it's almost never worth it.
Because what happens, the real way to do this, the real way to approach problems like that is not to say, oh, I can add this extra case to handle this thing.
It's to say, but why is symbolic slow?
Why is it ever slow?
So the real solution to this problem isn't that.
The real solution to this problem is to use the compiler, is to use the tinygrad compiler to generate the command queues.
Do you see what I mean by that?

##### **Hooved** [[00:35:58](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2158)]
I am talking about... I'm not talking about JavaScript at all.
I'm talking about everything I just said.
Right.
Sorry.
Right.
All right.
So you're talking deeper at the level of UOps and stuff.

##### **Geohot** [[00:36:14](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2174)]
What I'm always saying is if the thing that you're looking to do looks like adding complexity in exchange for speed, it's never worth it.
You should instead ask...
You should instead ask, why is this slow?
And how can I rewrite this whole thing so that it just doesn't matter?

##### **Hooved** [[00:36:36](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2196)]
I think I see what you're saying.
I'm glad I brought this up, so I won't spend time on that.

##### **Geohot** [[00:36:41](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2201)]
Yeah, there's no way something like that's ever going to be merged.

##### **Hooved** [[00:36:44](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2204)]
No, that's why I brought it up, and I'm really glad I did.
Thank you.
So I'll just focus on getting the graph without any of that extra complexity ready for review.
But I don't think that's going to take that long.

##### **Geohot** [[00:37:00](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2220)]
I don't really care about speed.
I really only care about correctness.
What's the right way to do this?

##### **Hooved** [[00:37:13](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2233)]
Yeah, I mean, if we don't care about speed, yeah, I'm not even sure how important the graph is, honestly.

##### **Geohot** [[00:37:22](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2242)]
This is what I'm saying.

##### **Hooved** [[00:37:23](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2243)]
Yeah.
Yeah.
I mean, maybe we don't even include the graph.
Okay.
Yeah.

##### **Geohot** [[00:37:32](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2252)]
So the thing that's much more valuable than okay, look, and if speed is 10x off, okay, that's a different story.

##### **Hooved** [[00:37:41](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2261)]
No, it's like, 0.5x, 50%.

##### **Geohot** [[00:37:44](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2264)]
Yeah, maybe worth it, but like, probably not.
The thing that I want to see come out of the WeBGPU project is I want to make it, like, for example, the whisper thing.
Some guy posted, hey, can we get whisper?

##### **Hooved** [[00:38:00](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2280)]
I saw that.
Yeah.

##### **Geohot** [[00:38:02](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2282)]
Like, that should be easy.
Making this usable for people is so much more valuable than making it 50% faster.

##### **Hooved** [[00:38:09](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2289)]
I agree.

##### **Geohot** [[00:38:10](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2290)]
Because if no one uses it, it doesn't matter how fast it is.
100%.

##### **Hooved** [[00:38:12](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2292)]
I'm 100% behind that.
OK, so you know what?
Maybe we don't even need the graph.
So that being said, the next topic is just getting the stuff into the library in a simple way as possible.
Really, the biggest headache there has been figuring out how to get the JavaScript stuff in.
I want to continue to attack that.
The one thing is, you mentioned you were going to refactor the JIT.
I think all that will depend on what that refactor looks like.
You mentioned last week maybe I could play with it, but I'm not quite sure what you want.
So I've hesitated to try to submit anything for that.
So it would be useful to know what the timeline is for that.
Or in terms of should I pause on trying to fit stuff in, like the JavaScript rendering?
or is it going to be done anytime soon?

##### **Geohot** [[00:39:21](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2361)]
It's not my highest priority, but here's a way to kind of go about this, right?
Like, you can use what exists in the JIT, but capture the sink.
Like, maybe the way to do the JIT refactor, what if you're just given the sink, right?
Do you have to even use the JIT for export?

##### **Hooved** [[00:39:49](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2389)]
What we need, and I've thought about this a little bit, what we need is to capture the kernel graphs across multiple realizes within a single compute pass, within a single forward pass of the model.

##### **SPEAKER_05** [[00:40:02](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2404)]
Wait.
So why does it have to be multiple realizes?
Can you co-realize?

##### **Hooved** [[00:40:08](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2404)]
That's an interesting point.
I haven't thought about that.
Maybe.
I don't know.

##### **Geohot** [[00:40:13](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2413)]
So my suggestion to approach this, I'm not going to be, the JIT refactor is pretty low on my priority list.
I'm not going to be able to do it for at least a few more weeks.
Like things like the multi-refactor are higher priority.
But so here's a way to think about this.
You don't need the JIT, right?
If you can get everything into one realize, it doesn't have to be a realize.
We've already exposed new functionality called kernelize.
And kernelize will group everything into kernels for you.

##### **Hooved** [[00:40:42](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2413)]
I understand.
I know what that looks like.
I've studied it.

##### **Geohot** [[00:40:46](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2413)]
Yeah, you might want to approach this whole thing like that, right?
Like, just don't use the JIT.
Don't use the JIT for webGPU export.
There's no reason that you have to.
There's no reason that you have to use the JIT for export.
You can just not use it.
That's probably how I'd go about this.

##### **Hooved** [[00:41:02](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2462)]
Yeah, maybe I'll look at that, and then I'm not convinced right now.
I mean, I trust you, but I'm just saying I don't completely understand that.
Maybe I'll iterate in Discord if you want me to look at that and approach it that way, just to make sure that my understanding is correct.
I might write something in the Discord to verify.

##### **Geohot** [[00:41:22](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2482)]
Well, I'm just saying like what I'll merge and what I won't merge.
Like if there's stuff that looks like a lot of changes to the JIT to like add new functionality kind of hacked into this old JIT thing, that stuff's really hard to merge.
But if it looks like a new code path that's using kernelize, if it looks like something that, like, here's a WebGPU exporter, and the WebGPU exporter doesn't use the JIT at all, it just takes in a function, takes in some test inputs, and runs the test inputs through the function, grabs the sinks at the end of the function, kernelizes that function, and then uses a graph rewrite rule to take that kernelized graph and convert it to JavaScript.
That's the way to do it.

##### **Hooved** [[00:42:03](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2523)]
Right, so the one thing that doesn't make sense is what does co-realizing mean?
Like in the Llama, you do a realize every time you write to the KV cache, so you'll have like 16 realizes in a Llama.
And then they're separated through time.
You can replace those realizes in the Lama with kernelize.
Yeah.
I think so.
It should work.
You can't use realize...
Yeah, but you can do kernelize multiple times.

##### **Hooved** [[00:42:35](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2555)]
Right.
No, I understand what you're saying there.
And then you have to paint them together.
Those are separate tensors.
Or are they?
No, I have to think about it.
Sorry.

##### **Geohot** [[00:42:51](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2571)]
Think about it.
They should all be in a graph.
And if they're not all in a graph, we should think about how they can be all in a graph.
I want to move away from supporting realizes in the middle of the JIT.
I want to move entirely toward every, yeah.

##### **Hooved** [[00:43:04](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2584)]
That's what I was missing.
Okay, now it's making sense.
Okay.

##### **Geohot** [[00:43:08](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2588)]
But you can use kernelize as many times as you want.
So everywhere you used to use realize, use kernelize.

##### **Hooved** [[00:43:14](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2594)]
All right, I'll try that, and I'll see if it makes sense.

##### **Geohot** [[00:43:18](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2598)]
Cool, and I would even merge that.
If you can fix Lama to have the same speed but not use those realizes and use kernelize, I would merge that.

##### **Hooved** [[00:43:25](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2605)]
All right, I think that'll be my highest priority.
Okay.
All right, thanks.

##### **Chenyu** [[00:43:34](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2614)]
So assigns are all good now?

##### **Hooved** [[00:43:37](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2617)]
Sorry, say again?

##### **Chenyu** [[00:43:39](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2619)]
Well, that was a question for I think we probably need to realize this big assign or partial assign.

##### **Geohot** [[00:43:48](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2628)]
Well, I don't know about that.
But I definitely made a change to assign this week.
Assign.
Assign used to be able to just be silently replaced by with replace.
And it still can, but it requires that it be contiguous now.

##### **Chenyu** [[00:44:05](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2645)]
Well, that's a different thing.
So I think, for now, the existing realize instance is for that partial in place assignment for kvcache.
That would be it.

##### **Geohot** [[00:44:17](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2657)]
Yeah.
Try kernelize.
Kernelize might just work.
And if it doesn't work, we've got to figure out why.

##### **Chenyu** [[00:44:24](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2664)]
Great.
I'm all for that.
All right.
OK, sounds good.
Let's move on.

##### **Chenyu** [[00:44:37](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2677)]
You briefly talked about unroll, A-range, diff.
But since the slide closes here, you want to say something?
So good work putting the Z3 OOB in.
It was pretty nice.

##### **Geohot** [[00:44:58](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2698)]
Oh, cool.
This looks ready to merge, too.
He marked it as not draft.
Maybe he's ready to talk.
But yeah, I mean, this PR looks great.
Passing test complexity with unroll, too.
Great.
I can merge this into my branch and get this done today.
And yeah, thanks for the help.

##### **Chenyu** [[00:45:31](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2731)]
Sounds good.
There was some discussion around CPU graph of LLVM graph.
I don't know what happened.

##### **Geohot** [[00:45:44](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2731)]
Yeah, I think that's where the bounty is going to go.
I mean, the bounty was for both.
Yeah, so yeah, no, I think, oh, this is, I'll lock this bounty.
Yeah, no, Cortis, the bounty will be yours if the LLVM graph stuff gets in.
Yeah, this looks good.
Yeah, I'll try to review this today, maybe tomorrow.
Oh, I know there's some debate about the always inline thing, too.
Is that OK?
Nimlgen you commented on that?

##### **Nimlgen** [[00:46:24](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2763)]
So yeah, I mean, all this in line should solve the problem.

##### **Geohot** [[00:46:32](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2763)]
Is it bad for some reason?

##### **Nimlgen** [[00:46:36](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2763)]
No, I think no.
I mean, the only bad thing is if we have several kernels within one graph, and they are repeated.
So they will just blow up the code base, yeah, because they're inlined.
And that's not a separate call.
But yeah, I think it should be fine.
We won't see any huge difference.

##### **Geohot** [[00:47:03](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2823)]
Yeah, that's OK.
It generates a bit more code.
Yeah, OK, yeah, it was going to merge this.

##### **Chenyu** [[00:47:25](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2845)]
We touched on the stable diffusion speed earlier.
So I think George already put a list of things that will help to make this example faster.
There's that.

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2859)]
Yeah, I don't have too much else to say on that.
We just got to get all these Fuse.
We got to find these scheduler bugs that are causing the Fuse softmax to be slower.
I think this is also why it got slower over BERT, because there's no reason otherwise to be slower.
It should be a huge win.

##### **Chenyu** [[00:48:11](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2891)]
Yeah, so I think for a specific kernel itself, it's faster because it's one or two less call per softmax.
But for some reason, it has ops to other stuff.

##### **Geohot** [[00:48:24](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2904)]
You know, there's some kind of scheduler bug that's causing some crazy n-squared behavior.
Yeah.

##### **Chenyu** [[00:48:34](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2914)]
That's kind of a reason why single kernel softmax didn't make it to BERT.

##### **Geohot & Chenyu** [[00:48:38](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2918)]
Yeah, yeah, yeah.
That's not good.
OK.
Other bounties?
So FP8 support?
Oh, yeah.
How's that one?
I commented on it a little.
Yeah, it's the same thing.

##### **Chenyu** [[00:49:12](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2952)]
So I don't exactly know how we want to handle these or, I guess, in future Dtype along with the Python backend.
Because for Python backend, we store Python float, right?
It's either we want to store it exact as a Python float somewhere, or as you suggest, find another that can preserve the whole exact information.
And every time when you load it, do some special thing.
I don't know.

##### **Geohot** [[00:49:49](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=2989)]
Yeah, I think that this approach is kind of fine, except that it's calling this function always, even if it's not an FP8.
I'm just like, I'm not happy with the code quality of this PR.
I never have been.
Like he makes the change.
And it's like, it's right.
It's not wrong.
But it's like, why is now it calling with FP8 handling for every other Dtype?
There's all these, like, or Dtype is in FP8s kind of stuff.
Like, no, this should just be abstracted so much better.
I don't want to merge this.
There's way too much, like, custom crap in here for FP8, and I really think it doesn't have to be like that.
Like, that one I know doesn't have to be like that, because I asked for it.
And I spent time thinking about how to actually do this.
And the right way to do it is, when you're doing an ALU, you check...
Yeah, right?
This isn't even with FP8 handling.
No, exec ALU should just do this.
Exec ALU should just handle the Dtype thing.
Yeah, this is crappy code.
Like exec ALU, sure, you can have some Dtypes that are just like, yeah, I agree that it's a decision that we have to make, right?
Like when you have an FP8 in Python, should that FP8 be what should it be?

##### **Chenyu** [[00:51:23](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3083)]
I think it's a similar thing that we currently, I think we previously support, but we currently don't support say BF16 with Python backend.
And it's the same problem as if I don't do any ALU, I just create a tensor with Bfloat16 and some numbers.
Say if that number is larger than
BF16 max, but smaller than the max for float32.
And we store that.
Just create a tensor, and we just call the dot data immediately.
Should that stay in the float limit, or should that be like infinity because of truncation code somewhere?
Stuff like that.

##### **Geohot** [[00:52:10](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3130)]
I agree that these are definitely decisions that we have to make.
But they should not be like,
The decisions need to be made in one place.
It shouldn't be spammed all over the code base.

##### **Chenyu** [[00:52:23](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3140)]
Yeah, that's for sure.
Cool.
Any suggestion for how to make this merge-able?
I mean, we definitely don't merge this, but I also don't...
OK, I'll think about it.

##### **Geohot** [[00:52:53](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3173)]
Yeah, I don't have a solution off the top of my head.
But I'm looking at it, and there's way too much spam.
And these should be refactors and not spammed everywhere in the code base.

##### **Chenyu** [[00:53:03](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3183)]
Yeah, I think a good approach might be we just find a way to support the BF16 and say similar to that.
Maybe that's easier.
Because I think from...
We want to find more contributors, and it's better if we can give them the good things to follow.

##### **Geohot** [[00:53:27](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3207)]
No, I know.
I know.
And yeah, some of this I do blame on us.
And he's definitely trying.
But it's like, there are core refactors missing here.
And yeah, maybe it's too much to ask for external contributors to come in and say, wait, no, this actually has to be refactored.
You just can't keep doing things like this.
So yeah, I think that makes sense if you want to support bfloat16.

##### **Chenyu** [[00:53:51](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3231)]
I'll comment on this.
I'll think more about that.
And if it's a core decision we need to make, we can discuss it sometime.
Are we all done with all the average pool 3D or linearizer failure 53?

##### **Geohot** [[00:54:16](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3256)]
Yes, yes.
Oh, I don't know about 53, but the average pool 3D failure.
Yeah, again, like I commented on that.
I'm not going to merge this or.
Like it was fixed by.
Yeah, I fixed it.
Yeah.
It was like this fix adds code.
You never needed to add code, which I actually post the fix that fixes it.
Yeah.
I just moved where you changed the unparented reduces.

##### **Chenyu** [[00:54:49](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3282)]
Do you know what causes that value?

##### **Geohot** [[00:54:55](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3295)]
No.
I don't really know what the bug was.
I think that what was happening is all of those reduced things were in symbolic, were in a whole symbolic thing.
So I think they were triggering at unexpected times.
because we add the symbolic thing to so many different places.
So now it's just in that one place.
I have one PMReduce that handles the reduce stuff.
That's what does all the collapse stuff as well.
And yeah, just moving it there and just writing the code in a tighter way fixed that bug.

##### **Chenyu** [[00:55:29](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3329)]
Maybe bug somewhere else.
Because you will expect, however slow or bad you combine these rules, it shouldn't be wrong.

##### **Geohot** [[00:55:40](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3340)]
Well, yes and no.
I think that like, probably what was happening is this thing was like happening too early or something.
I agree that there could still be a bug somewhere else.
And this could have just masked it.
But I mean, now we don't have a test anymore to test it.
So yeah, no, I don't know.
I found another linearizer bug.
There's a third linearizer.
There are definitely still linearizer bugs, especially as we get into these fused patterns.
They get weirder and weirder and weirder.
But at least now the linearizer is really easy to reason about, so they're easy to fix.
And every time we add like a new set of, oh, just check the back ends and check these counts.
And like most of the time, things that look like this are wrong.
And there's a fundamental bug that underlies everything.
Like I remember last time in the old linearizer, I added this whole big hack to like deal with like, oh, like reparenting things.
And like, you don't need any of it.
You just need to write it correctly.

##### **Chenyu** [[00:56:47](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3407)]
I think any time in tinygrad, if there's a function called fix up something or re- something, something,
It's always bad.

##### **Geohot** [[00:57:01](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3421)]
Yeah.
But overall, things are getting simpler.
I'm happy with the A range change.
Yeah, no, things that look like that are just going to.
The A-range thing, oh my god, that function had so many bugs in it.
That function was like, oh, check them all, and if it's negative, if it's positive.
No, it's the same.
It's just what you've done is you've taken four rules and merged them into one rule.
Every time you can use tinier rules, it seems to just work a lot better.

##### **Chenyu** [[00:57:33](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3453)]
Yeah.
How serious are we to make Z3 a dependency?

##### **Geohot** [[00:57:42](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3456)]
I haven't seen something that requires it yet.
I would rather not.
But if there's something that just really requires that, then yeah, OK, we require it.
I thought I required it for the A. I tried to use it for the Arange stuff, but it can't really do that.

##### **Chenyu** [[00:58:15](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3456)]
I see.
OK, sure.
That's better.

##### **Geohot** [[00:58:15](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3495)]
Yeah, no, it's not really.
Yeah, there's things that it's a constraint solver.
It's not like a program simplifier.

##### **Chenyu** [[00:58:26](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3500)]
I mean, you can use that to write and row Arange div?

##### **Geohot** [[00:58:33](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3500)]
Oh, A range div, of course, yes.
But what you can't use it to do is like loop reduction.
It doesn't have an O of one way of saying this thing can be all these values.
I was looking for something in Z3 that looked like sigma, and it doesn't really have that.

##### **Chenyu** [[00:58:54](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3534)]
Didn't TBT just say that's undecidable or something?

##### **Geohot** [[00:58:58](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3538)]
It's undecidable, yeah.
But actually, hmm, interesting.
You're right.
We could just use it for things like fold unrolled divs, and maybe we should.

##### **Chenyu** [[00:59:13](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3553)]
I think similarly, it's probably not really required now.
Let's see if we have a stronger use case for that.

##### **Geohot** [[00:59:21](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3561)]
Yeah, yeah.
We shouldn't shy away from it.
We shouldn't shy away from using it if there's, yeah.

##### **Chenyu** [[00:59:30](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3575)]
OK, sounds good.
I think that's it for this week.
We want to move this meeting a few hours back to accommodate more people in California.
It's like 7 AM.
I don't know how many people can really make it.

##### **Geohot** [[00:59:56](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3596)]
Yeah, what time did it used to be?

##### **Chenyu** [[01:00:00](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3596)]
I think back by two hours.
So that would be midnight for Hong Kong time.
Yeah, that sounds good.
If zibokapi is good with that.
Oh, OK.
So we will move.
OK, sounds good.
So we will move this meeting to 2 o'clock late.
So it will be 9 AM for West Coast time.
And I'll update the event in Discord as well.
We will know.
And what's that?
That's this meeting.
See you next week.

##### **Geohot** [[01:00:43](https://www.youtube.com/watch?v=9_7IhCYt1Kw&t=3643)]
Bye!
