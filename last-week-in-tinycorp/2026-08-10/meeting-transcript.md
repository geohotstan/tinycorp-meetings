# 2026-08-10 Meeting

### Meeting Agenda

**Time:** new meeting #32, 8/10 9am Monday San Diego time
- why is SLICE still here?
- why is LLaMA not faster?
- why is GPT-OSS not faster?
- why is HCQ not deleted yet?
- why is rangeify still long and confusing?


### Audio

[Youtube Link](https://www.youtube.com/watch?v=MbgtBg3gKSU)

### Highlights

- **[CI Stability](#geohot-000093)**: Geohot wants CI to run in under one minute and never fail, including benchmarks; two AMD CI runners are currently down, and CI instability is slowing development for everyone. 

- **[SLICE Removal](#chrism-000152)**: Chrism decides to remove SLICE without pursuing the variable-offset approach, after repeated test and benchmark failures; Geohot agrees that deleting the UOp will reduce the system's complexity. 

- **[Gitea CI](#geohot-000287)**: Geohot proposes moving internal runners to Gitea while keeping GitHub Actions for GitHub workflows, with the immediate goal of getting Docker-based CI below one minute and eliminating CI flakiness. 

- **[LLaMA Performance](#qazalin-000375)**: Qazalin reports that LLaMA is nearly 10% faster than the previous sprint, but the total runtime improved by only two minutes because the run converged one evaluation step later; the current gap to AMD is 79 ms. 

- **[LLaMA Bottlenecks](#qazalin-000482)**: Qazalin identifies exposed/idle time as a remaining performance issue and explains that the biggest kernel-level opportunities are Flash Attention and elementwise reductions, while SDMA has become less important after recent fixes. 

- **[AITER Integration](#qazalin-000700)**: Qazalin explains that AMD uses AITER for Flash Attention while tinygrad currently uses HipKittens; he says AITER kernels can be integrated through the existing HCQ argument mechanism and that an LLM can already convert the kernel calls into tinygrad's style. 

- **[GPT-OSS Performance](#wozeparrot-001431)**: Wozeparrot reports GPT-OSS at 1.65 seconds per step, with 1.3 seconds previously achieved using Prime Intellect; he says remaining work is largely kernel-related, including missing Flash Attention/sliding-window attention. 

- **[GPT-OSS September Target](#wozeparrot-001592)**: Wozeparrot believes the team can reach 1.3 seconds per step this sprint, while Geohot notes that this would still leave the overall run around 4:40 versus AMD's 128-minute target and asks for a complete plan to determine whether the September goal is achievable. 

- **[HCQ Deletion](#nimlgen-001750)**: Nimlgen says HCQ deletion is blocked by HCQ2-related benchmark failures; the CPU also needs copy-kernel support to finish its HCQ2 migration. 

- **[HCQ2 Migration](#nimlgen-001890)**: Nimlgen expects HCQ to be deleted by the end of the sprint, with only a handful of multi-tensor CI failures remaining; CPU enqueue overhead should also improve after the CPU fully migrates to HCQ2. 

- **[Multi-Machine Training](#geohot-002155)**: Geohot says he will handle the machine networking and asks Nimlgen to focus on deleting HCQ this sprint, with multi-machine training becoming the focus of the next sprint. 

- **[Qwen3.6](#geohot-002774)**: Geohot reports state-of-the-art Qwen3.6 performance on AMD, with merging targeted for this sprint; the main remaining custom-kernel dependencies are Flash Attention, Gated DeltaNet, and linear kernels where BEAM is not finding WMMA. 

- **[Rangeify Redesign](#geohot-002877)**: Geohot plans to focus on rangeify fixes, replacing the early single-point buffer-placement decision with a late-stage approach that inserts potentially unnecessary buffers and removes them later when it can determine which are actually required. 

- **[RDNA3 Assembly](#raine-003089)**: Raine reports that the RDNA3 assembly backend is down to six CI tests and under 600 lines of code; GEMM performance has improved by about 10%, although CI runtime remains unexpectedly slow. 

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=0)]
But, you know, when we have a lot of red X's on CI, everybody just thinks red X's on CI are acceptable.

##### **Geohot** [[00:00:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=10)]
So we got to fix this.

##### **Chrism** [[00:00:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=13)]
Is this the same like GPU falling off the bus issue? Because last time I mentioned this.

##### **Geohot** [[00:00:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=19)]
I mean, this looks more like an HCQ2 issue.

##### **Geohot** [[00:00:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=29)]
MLPerf AMD. And then how many of our runners are up right now?

##### **Geohot** [[00:00:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=42)]
Alerts for this, Wozeparrot?

##### **Geohot** [[00:00:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=48)]
Yeah, we have two of our AMD CI runners down right now.

##### **Geohot** [[00:00:54](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=54)]
It's really important that we get CI to be stable. You know, it just lowers development velocity for everybody else when it's not.

##### **Geohot** [[00:01:07](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=67)]
Yeah, I've been working on the Gitea thing.

##### **Geohot** [[00:01:15](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=75)]
I split the unit tests into platform tests.

##### **Geohot** [[00:01:23](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=83)]
Platform tests are stuff that needs like Windows or Mac.

##### **Geohot** [[00:01:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=88)]
Unit tests can run Linux.

##### **Geohot** [[00:01:33](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=93)]
I want to get our CI to be under one minute and never fail. And that's including benchmark. We just can't have CI.

##### **Geohot** [[00:01:46](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=106)]
Launching the Chestnut this week.

##### **Geohot** [[00:01:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=110)]
Whoever's working... I don't know if the person working on the NVIDIA stuff is in here, but I will send you a free Chestnut if you'd like.

##### **Geohot** [[00:02:00](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=120)]
The Chestnuts are unbrickable, which is cool.

##### **Geohot** [[00:02:08](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=128)]
Yeah, so there's that.

##### **Geohot** [[00:02:12](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=132)]
Yeah, and that'll fix your bricking issue. It looks like we can support Nvidia over USB 3.0, even though it might be a little slow to boot.

##### **Geohot** [[00:02:24](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=144)]
So yeah, with that, let's start with the first meeting item. Why is SLICE still here?

##### **Chrism** [[00:02:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=152)]
Yeah, I don't know. So I can remove it. And I think this is what I'm going to do today: just remove it without trying to do the variable-offset thing. I was running into a lot of issues where I would get all the tests to pass, push the benchmarks, and then a whole bunch of stuff would fail. I would change something, and it felt like that kept happening over and over with small things. The most recent thing was that BEAM, when it runs this, needs to allocate the buffers to test the kernels on, and then it would allocate the whole 24 GiB buffer. Yeah, I understand.

##### **Geohot** [[00:03:07](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=187)]
Okay, maybe you can do it the other way. Yeah, let's just get that merged. Let's get SLICE deleted. Every UOp we delete, every time we can make the spec a tiny bit cleaner, you're reducing something that is N-squared in complexity.

##### **Geohot** [[00:03:21](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=201)]
Because every op... So our op size is N-squared complexity. Because every op can sit on top of every other op. You always have to think for every op, what's its interaction with every other op. And that's N-squared. So every time we can lower the number of ops, we're lowering something that's N-squared.

##### **Chrism** [[00:03:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=225)]
Yeah. No, in retrospect, I should have just done this from the first place, because I actually had code that was mergeable that would remove slice.

##### **Chrism** [[00:03:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=233)]
That didn't have the variable thing. I should have just done that.

##### **Geohot** [[00:03:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=235)]
Great. Well, we can document the variable thing, and we'll think about that later. Yeah. Yeah, and then I want you back on CI. Yeah.

##### **Geohot** [[00:04:03](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=243)]
So for the GitHub, Gitea CI, Gitea has two images. It has a base image and then it has a full image. So the full images work. But what we should just do is have a Dockerfile. What was the downside to just having one Docker image that doesn't have to pre-install anything?

##### **Chrism** [[00:04:22](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=262)]
It was really... It was really slow to clone even on the namespace runners. But I think if we do it on our own stuff, then we can probably just have it set up already.

##### **Geohot** [[00:04:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=270)]
Yeah. Yeah, I think that the right way to do this is just... I don't know. I don't want to deal with namespace or GitHub actions. I mean, this still has to work on GitHub actions. But I think we can get rid of namespace entirely and just move our runners to here.

##### **Geohot** [[00:04:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=287)]
And we can have them only work on Gitea. And we can move GitHub back to just GitHub Actions. So it needs to run on GitHub with GitHub Actions. Yeah. But everybody internally here can move to Gitea. Yeah. And then we'll see what to do about benchmark. Right now, you'll have to use GitHub if you want to push to benchmark. If you're just doing stuff like the unit-test CI, that should be very fast on Gitea. Yeah. And we need to figure out how to...

##### **Chrism** [[00:05:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=318)]
Yeah, and I bet there's some way we can set this up intermittently to...

##### **Chrism** [[00:05:23](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=323)]
I don't know. I'm just interested about how we're going to do pull requests on both sites. Or if we're just going to move everything.

##### **Geohot** [[00:05:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=328)]
Yeah, I don't know about that.

##### **Geohot** [[00:05:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=332)]
We'll see. But the first step is just getting CI to be under a minute with Docker. And all of this CI flakiness. We need to really be on top of this.

##### **Geohot** [[00:05:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=345)]
It's frustrating for everybody.

##### **Geohot** [[00:05:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=348)]
Okay. Anything else?

##### **Chrism** [[00:05:52](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=352)]
No, not really.

##### **Geohot** [[00:05:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=355)]
Cool. So SLICE is gone today?

##### **Chrism** [[00:05:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=356)]
Yeah.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=356)]
Great. Okay. Why is LLaMA not faster?

##### **Qazalin** [[00:06:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=361)]
LLaMA is faster.

##### **Qazalin** [[00:06:05](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=365)]
I'll share the chart. This is comparing with last sprint.

##### **Geohot** [[00:06:12](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=372)]
All right.

##### **Qazalin** [[00:06:15](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=375)]
All right. For some reason, my runs converged one eval step later. So I think this is the seed thing.

##### **Qazalin** [[00:06:24](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=384)]
Maybe if we find a better seed, we can converge in the same number of steps.

##### **Geohot** [[00:06:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=389)]
I don't think we should be messing with seed. But yeah. So how is it? How is it? You know, it's almost 10% faster, yet the runtime only reduced two minutes.

##### **Qazalin** [[00:06:40](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=400)]
Because it took more steps to converge.

##### **Geohot** [[00:06:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=404)]
More steps to converge. Is this an FP4 thing?

##### **Qazalin** [[00:06:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=407)]
This is compared with FP4. It converged in the same number of steps as AMD. So even AMD converged in this number of steps.

##### **Geohot** [[00:06:59](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=419)]
And then what's the latest for where we're still spending time?

##### **Qazalin** [[00:07:05](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=425)]
Yes. I'll share that too. We are 79 milliseconds off from AMD.

##### **Geohot** [[00:07:16](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=436)]
Oh, so by the way, why it might be slower today, it's possible that it's hotter today.

##### **Qazalin** [[00:07:23](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=443)]
Oh, yeah. The machine got slower. Yeah. I know.

##### **Geohot** [[00:07:26](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=446)]
Yeah. I mean, that's one possibility. Another possibility is there's cruft on the machine that needs to be rebooted. Another possibility is there's a yeah. Okay. So plus means that's why we're slower.

##### **Qazalin** [[00:07:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=458)]
Yes. Plus means we are slower than AMD.

##### **Geohot** [[00:07:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=462)]
Oh, but okay. So there's no more scheduler issues.

##### **Qazalin** [[00:07:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=467)]
No more scheduler issues. We don't have to deal with this.

##### **Geohot** [[00:07:54](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=474)]
The SDMA thing is fine.

##### **Qazalin** [[00:07:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=476)]
SDMA thing is not fine because we're spending more time with idle.

##### **Qazalin** [[00:08:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=482)]
So our idle time is worse than AMD.

##### **Geohot** [[00:08:05](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=485)]
Yeah, but on the thing you just posted, it says idle is zero milliseconds.

##### **Qazalin** [[00:08:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=493)]
"Idle" here means SDMA and compute combined: whenever compute is not busy but SDMA is busy waiting for compute.

##### **Qazalin** [[00:08:27](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=507)]
The main thing is that we have more exposed time. So we have more time where we're just sitting and not doing anything.

##### **Geohot** [[00:08:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=518)]
Ah, well, that's not, like... Yeah, that's not reflected in this.

##### **Qazalin** [[00:08:43](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=523)]
Yes, this is focused on the kernels. If I copy their Flash Attention and I copy their GEMM, and I copy their optimizer... They have another optimizer thing. They have something similar to our FUSE_OPTIM.

##### **Qazalin** [[00:09:06](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=546)]
Which isn't default for us.

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=549)]
What do you mean? You mean FUSE_OPTIM?

##### **Qazalin** [[00:09:12](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=552)]
Yeah, the distributed one.

##### **Geohot** [[00:09:16](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=556)]
Oh, they're doing some distributed stuff. Yes. Okay. So you have a few more. I'm sorry. Okay. I mean, so looking at this, I mean, looking at this, just going down and sorting, the top two things seem to be flash attention and element wise reductions.

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=574)]
Yeah.

##### **Geohot** [[00:09:37](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=577)]
But so like how important is it that I thought most of what this was going to be about was the SDMA stuff.

##### **Qazalin** [[00:09:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=585)]
So I fixed some stuff and idle time went down. Okay. So SDMA became less of a problem.

##### **Geohot** [[00:09:54](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=594)]
If it's something we don't have to deal with, I'm very happy not to deal with it. Especially until HCQ2 is a bit more stable. We definitely have a path to doing it. But it makes sense what they're doing. My understanding from what you posted is that there are two compute queues. On one compute queue, you have a small-global-size copy that's higher priority, so you can do that.

##### **Geohot** [[00:10:21](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=621)]
And that's just scheduling on CUs. It looks like it's something like four CUs is capable of copying.

##### **Geohot** [[00:10:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=630)]
Yeah, I mean, that's going to be some hit to performance, but only like 2% or something.

##### **Geohot** [[00:10:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=642)]
Like there's a question of how many CUs can saturate the PCIe bandwidth.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=648)]
And if that's small enough, then you can do that. Yeah, just using CUs and not using the SDMA engine seems kind of nice, because then we could do fancier collectives. We could do collectives that actually do the math right away and don't have to round-trip that to global memory, right? The SDMA engine is only capable of writing to global memory, so you have to write to global memory, wait for it to finish, and then do the actual reduce, versus if you can just read from another thing.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=679)]
Yeah, you definitely get that there. But if you think we can beat AMD's time just by... I mean, these things all stack. So yeah, if we could just improve Flash Attention, elementwise... You have 16 GEMMs.

##### **Geohot** [[00:11:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=698)]
We're using HipKittens now for Flash Attention.

##### **Qazalin** [[00:11:40](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=700)]
We are using HipKittens.

##### **Geohot** [[00:11:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=702)]
What's AMD using?

##### **Qazalin** [[00:11:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=704)]
AMD is using AITER, which is like ROCm.

##### **Geohot** [[00:11:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=709)]
Can we make it easy to call AITER kernels?

##### **Qazalin** [[00:11:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=715)]
Yes, it's going to be the thing that I showed you when we were in Hong Kong last time. The HCQ args thingy.

##### **Geohot** [[00:12:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=722)]
What HCQ args thingy?

##### **Qazalin** [[00:12:04](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=724)]
So like the struct that we use for the arguments of the kernel.

##### **Geohot** [[00:12:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=731)]
Oh, yeah.

##### **Qazalin** [[00:12:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=733)]
Yeah, you need like an arbitrary pointer.

##### **Geohot** [[00:12:15](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=735)]
Yeah,

##### **Qazalin** [[00:12:16](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=736)]
yeah,

##### **Geohot** [[00:12:16](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=736)]
yeah.

##### **Qazalin** [[00:12:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=738)]
But I can probably survive doing this, because right now we're using the MXFP4 GEMM from AITER.

##### **Qazalin** [[00:12:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=749)]
Yeah, I just have an LLM convert it to our style of calling the kernels. That works.

##### **Geohot** [[00:12:39](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=759)]
Yeah, that might be fine. As long as there's not too many of them.

##### **Geohot** [[00:12:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=765)]
How much of this is on master? What's the time on master right now?

##### **Qazalin** [[00:12:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=768)]
Time on master? Master is 1.48 as of today.

##### **Geohot** [[00:12:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=775)]
So where's the gap?

##### **Qazalin** [[00:13:00](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=780)]
The gap is all-reduce.

##### **Geohot** [[00:13:05](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=785)]
Where's your PR that has the fixes for all-reduce?

##### **Qazalin** [[00:13:09](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=789)]
There is no PR. I can open one.

##### **Geohot** [[00:13:14](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=794)]
What do the fixes look like? Are they mergeable, or are they...?

##### **Qazalin** [[00:13:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=799)]
They're not mergeable. They're slop. I need to fix them and clean them up.

##### **Geohot** [[00:13:24](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=804)]
Are they fixable in theory?

##### **Qazalin** [[00:13:27](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=807)]
Oh yes, they are principled fixes. They're mostly like: if you have a SHRINK and then a COPY, use a SLICE, or SHRINK once SLICE is gone. Or if you're doing an all-reduce, don't make copies; just directly all-reduce into the buffer that you want to all-reduce.

##### **Qazalin** [[00:13:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=829)]
Yeah, I mean, a lot of these are just assigning to a temporary and then assigning that temporary back to the buffer, where it's like a STORE thing.

##### **Geohot** [[00:13:59](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=839)]
Yeah, okay. Maybe work on the kernels for now. Maybe this will be easier with the new rangeify stuff.

##### **Qazalin** [[00:14:07](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=847)]
Yes, I could merge the custom-kernel CONTIGUOUS removal, which helped.

##### **Qazalin** [[00:14:12](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=852)]
For the other ones, probably all the same thing.

##### **Geohot** [[00:14:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=857)]
Yeah, the custom-kernel CONTIGUOUS change is good.

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=864)]
That's universal. That doesn't affect rangeify because that's changing the input graph.

##### **Geohot** [[00:14:34](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=874)]
But yeah. So, okay, good. Sounds like we just have a bunch of kernels to work on.

##### **Geohot** [[00:14:43](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=883)]
These kernels are ASM? Yeah. Well, that's annoying.

##### **Geohot** [[00:14:51](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=891)]
There's no hope of trying to express them in our stuff?

##### **Geohot** [[00:14:59](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=899)]
Of course.

##### **Qazalin** [[00:15:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=902)]
I don't think so, because you have to go through LLVM.

##### **Geohot** [[00:15:07](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=907)]
You mean you have to go through LLVM?

##### **Qazalin** [[00:15:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=910)]
Yeah. I mean, if you express it in our stuff, right?

##### **Geohot** [[00:15:16](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=916)]
No, but is AITER... Are these kernels open source? Like, how does AITER work?

##### **Qazalin** [[00:15:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=928)]
They have a similar DSL to us in Python.

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=934)]
I see.

##### **Qazalin** [[00:15:36](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=936)]
It's a little uglier than ours, but it exists.

##### **Geohot** [[00:15:40](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=940)]
For assembly.

##### **Qazalin** [[00:15:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=942)]
For assembly. And they just, like...

##### **Geohot** [[00:15:46](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=946)]
Can you link to one of these kernels?

##### **Qazalin** [[00:15:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=949)]
But actually, for these kernels, they don't have an open-source compiler. They just ship the binary.

##### **Qazalin** [[00:16:00](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=960)]
That's the Flash Attention blob.

##### **Geohot** [[00:16:03](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=963)]
Oh.

##### **Qazalin** [[00:16:04](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=964)]
That's my impression of some of these faster kernels.

##### **Geohot** [[00:16:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=970)]
Okay, so there isn't...

##### **Qazalin** [[00:16:14](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=974)]
There's only the proprietary compilation process that makes this. It's the blob of the Flash Attention kernel for this head size.

##### **Geohot** [[00:16:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=985)]
I see. So it's like that kind of crap.

##### **Qazalin** [[00:16:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=990)]
Yes. And what I did is just, like, disassemble it.

##### **Geohot** [[00:16:33](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=993)]
These .co files are just compiled?

##### **Qazalin** [[00:16:37](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=997)]
Yes.

##### **Geohot** [[00:16:41](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1001)]
Yeah.

##### **Geohot** [[00:16:43](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1003)]
I mean, how nice... if you tell an LLM to take one of these kernels and just use our ASM syntax and make it as nice as possible, how nice does it get?

##### **Qazalin** [[00:16:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1013)]
The MXFP4 GEMM is an example.

##### **Qazalin** [[00:16:57](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1017)]
So this is our MXFP4 GEMM in master.

##### **Qazalin** [[00:17:04](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1024)]
The kernel class is copied from AMD assembly.

##### **Geohot** [[00:17:07](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1027)]
I mean, this is massive. How much of this can we... Yeah.

##### **Geohot** [[00:17:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1033)]
How much... if you just tell an LLM to iterate on it... And this only works on the MI350?

##### **Qazalin** [[00:17:24](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1044)]
Tile sizes, you mean? Yes. Tile sizes are kind of hardcoded.

##### **Geohot** [[00:17:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1050)]
Does it work in our emulator?

##### **Qazalin** [[00:17:33](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1053)]
This one, I haven't tried on our emulator, but I think it should work.

##### **Qazalin** [[00:17:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1058)]
I mean, the emulator code is basically: I just tell Codex if it doesn't work, and it fixes it. There's not a fundamental issue with the emulator.

##### **Geohot** [[00:17:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1068)]
Uh... Yeah, no, that's good. Yeah, let's get these up and working in the emulator.

##### **Geohot** [[00:17:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1073)]
And let's get them cleaned up as much as possible as we start to migrate the rest of the kernels.

##### **Qazalin** [[00:18:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1081)]
Yeah, I think what I would do is get these state-of-the-art kernels as clean as possible in our DSL, and then we'll figure out how to express this in higher and higher-level stuff.

##### **Geohot** [[00:18:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1091)]
Cool. But, you know, I want them all running in our emulator.

##### **Geohot** [[00:18:15](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1095)]
I want to make sure they all work. Yeah, I want this stuff in CI. We need a very clean kernel library. This seems like a place where we can beat AMD if these AITER things are actually closed-source.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1109)]
Are they actually?

##### **Qazalin** [[00:18:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1112)]
They are. That's my impression.

##### **Qazalin** [[00:18:37](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1117)]
A lot of these are just, like, literally...

##### **Geohot** [[00:18:40](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1120)]
Yeah.

##### **Qazalin** [[00:18:41](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1121)]
...attention, head-size, .s, .bin, or .so, or whatever. Not even .so. Yeah.

##### **Geohot** [[00:18:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1128)]
Yeah, that's .co.

##### **Qazalin** [[00:18:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1130)]
Yeah.

##### **Geohot** [[00:18:51](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1131)]
Let me quickly... Is this really...

##### **Qazalin** [[00:18:54](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1134)]
There are some for loops in here. I mean, that's the best it can do. I didn't push it too much, but I think it can make nice functions and make it readable, as readable as ASM can get. I think your SGEMM was pretty readable at some point. Yeah.

##### **Geohot** [[00:19:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1158)]
The ASM GEMM that I wrote for RDNA3 is pretty readable.

##### **Geohot** [[00:19:33](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1173)]
Oh, it says the kernels are fully open-source.

##### **Qazalin** [[00:19:40](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1180)]
It's a binary that's...

##### **Geohot** [[00:19:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1184)]
I see the binary's committed, but I don't... I wonder if they can be compiled.

##### **Geohot** [[00:19:58](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1198)]
.bind, host launcher, kernel body.

##### **Geohot** [[00:20:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1211)]
Is it this?

##### **Qazalin** [[00:20:20](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1220)]
These are HIP.

##### **Qazalin** [[00:20:23](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1223)]
This is composable kernel stuff.

##### **Qazalin** [[00:20:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1230)]
Like, there's a whole other repo that's only assembly.

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1237)]
It's in either... It's in the HSA stuff, or...

##### **Qazalin** [[00:20:43](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1243)]
I'll see if I can find it. But these are... Okay.

##### **Geohot** [[00:20:51](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1251)]
No, I mean, these do seem closed.

##### **Wozeparrot** [[00:20:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1256)]
From what I understand, AITER has multiple backends that it can call kernels through.

##### **Geohot** [[00:21:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1261)]
Mm-hmm.

##### **Wozeparrot** [[00:21:05](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1265)]
Yeah. Composable Kernel is one backend, and then the hand-tuned ASM stuff is another one. I believe they recently added HipKittens as well.

##### **Geohot** [[00:21:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1279)]
This repo has at least five distinct Flash Attention implementations, each with different backends. That's what GLM is saying.

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1288)]
Mm-hmm.

##### **Geohot** [[00:21:31](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1291)]
Cool. So we'll just keep... Find the fastest kernels, get them in, and then we'll get our assembly backend eventually generating them.

##### **Geohot** [[00:21:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1304)]
Yeah, so that's what's happening.

##### **Qazalin** [[00:21:46](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1306)]
Actually, like, one other thing I would mention is that our quantizer is getting better than theirs.

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1312)]
Right. Is it really? Yeah, it is. What's it written in?

##### **Qazalin** [[00:21:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1315)]
Oh, it's in HIP. But I think what I can do is, because every kernel is written in one backend, I can easily fuse stuff.

##### **Qazalin** [[00:22:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1330)]
Or they don't fuse a lot of these things. Like, they have a different SwiGLU, and then they just write to global memory. It's all just going to global memory.

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1337)]
Yeah, yeah.

##### **Geohot** [[00:22:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1339)]
I mean, the next project for all of this is going to be like, I want to get these kernels in, I want to make them fast, and then we have to figure out how to get our stuff generating these kernels. And we're going to do it from the bottom. We're going to move up layer by layer. Right, so right now we're expressing it in raw assembly, but can we express it in assembly and let it do the register allocation?

##### **Geohot** [[00:22:39](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1359)]
Right, then can we move up to instruction selection? Right, can we let it do register allocation? Can we let it do linearization? Can we let it do instruction selection? I want to, like, move back one step at a time.

##### **Geohot** [[00:22:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1373)]
Through everything.

##### **Geohot** [[00:22:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1375)]
Until these kernels are expressible in just full tinygrad.

##### **Geohot** [[00:23:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1382)]
But yeah, that's why it's important: any kernel we use, I want to make sure it works in the emulator and is tested in CI.

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1391)]
But cool. So this sprint seems like it's going to be a kernel migration sprint.

##### **Qazalin** [[00:23:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1399)]
All right.

##### **Geohot** [[00:23:22](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1402)]
Cool. Yep.

##### **Geohot** [[00:23:31](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1411)]
Anything else?

##### **Qazalin** [[00:23:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1415)]
That's all.

##### **Geohot** [[00:23:37](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1417)]
Okay. Why is GPT-OSS not faster?

##### **Wozeparrot** [[00:23:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1422)]
We are faster.

##### **Geohot** [[00:23:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1424)]
No, we are at 5:50.

##### **Geohot** [[00:23:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1427)]
We're at 5:50?

##### **Wozeparrot** [[00:23:51](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1431)]
It's 1.65 seconds a step.

##### **Geohot** [[00:23:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1435)]
1.65 seconds a step. So you met the target, which is good. Now, where's our next target?

##### **Wozeparrot** [[00:24:08](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1448)]
I think before you killed Kimi, I had Prime Intellect running.

##### **Wozeparrot** [[00:24:15](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1455)]
And it got to 1.3 seconds a step.

##### **Geohot** [[00:24:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1459)]
Oh, Kimi's back, by the way. Sorry about that.

##### **Wozeparrot** [[00:24:23](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1463)]
It's okay.

##### **Geohot** [[00:24:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1465)]
You can also use my... I posted a Kimi token in employees. You can use it with the real Kimi if you want that. But okay, so you got it to 1.3.

##### **Wozeparrot** [[00:24:33](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1473)]
Yeah, there's still a bunch of kernel stuff that needs to happen.

##### **Geohot** [[00:24:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1487)]
And is this 5:50 on master?

##### **Wozeparrot** [[00:24:54](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1494)]
It is just missing some Flash Attention stuff, or sliding-window attention.

##### **Geohot** [[00:25:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1501)]
Maybe, yeah, maybe we get this merged and then figure out where you think we can get to next sprint.

##### **Geohot** [[00:25:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1510)]
And then also, let's figure out if we're actually on track to meet AMD's target or if there's any fundamental reason why we just can't.

##### **Wozeparrot** [[00:25:22](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1522)]
We should be on track. I asked a couple LLMs if we're fundamentally off, and none of them said we are fundamentally off.

##### **Geohot** [[00:25:31](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1531)]
The LLMs think we can eventually get to the target?

##### **Geohot** [[00:25:36](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1536)]
Yeah.

##### **Geohot** [[00:25:40](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1540)]
Yeah. 128 minutes.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1548)]
At 350 minutes, we've got to get to 128.

##### **Geohot** [[00:25:58](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1558)]
We're almost 3x off. We got to be missing some major things.

##### **Wozeparrot** [[00:26:06](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1566)]
As far as I can tell, and as far as the LLMs can tell, there's nothing major actually missing. It's just that our GEMMs don't hit great peak.

##### **Geohot** [[00:26:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1578)]
And then we have a bunch of fusion misses.

##### **Geohot** [[00:26:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1585)]
Can we get a breakdown of where everything is? What do you think we can get to this sprint?

##### **Wozeparrot** [[00:26:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1592)]
I think we can get to 1.3 this sprint.

##### **Geohot** [[00:26:36](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1596)]
1.3.

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1599)]
Which will be what total time?

##### **Geohot** [[00:26:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1607)]
It's 12...

##### **Geohot** [[00:26:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1610)]
4:40.

##### **Geohot** [[00:26:54](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1614)]
4:40. Yeah. And this doesn't seem like we're on track.

##### **Geohot** [[00:27:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1622)]
We have to have this done by like September.

##### **Wozeparrot** [[00:27:08](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1628)]
Yeah.

##### **Geohot** [[00:27:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1630)]
I think... I mean, do you have a full plan for the target we need to hit? Put together a full plan for the target we need to hit every sprint in order to actually meet this target. Because if we can't meet this target, we're just wasting time. We're not getting paid anything. We're not getting anything for...

##### **Geohot** [[00:27:27](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1647)]
Partial.

##### **Wozeparrot** [[00:27:34](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1654)]
Okay.

##### **Geohot** [[00:27:37](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1657)]
Give a full... Like, I want to see a full plan for by the end of September.

##### **Geohot** [[00:27:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1664)]
If we don't think we can do this by the end of September, is this just a waste of time?

##### **Geohot** [[00:27:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1669)]
Because, yeah, we get nothing for partial...

##### **Wozeparrot** [[00:27:59](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1679)]
Yeah, it's just a little unclear to me how much certain things will save.

##### **Geohot** [[00:28:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1691)]
Well, yeah, if you could today just put together a plan, put together a plan that you're confident in that we can actually get to by the end of September or say, hey, look, I just don't think we can do this.

##### **Geohot** [[00:28:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1705)]
Because, yeah, there's no point if we get this down to three hours, it just doesn't matter.

##### **Wozeparrot** [[00:28:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1710)]
Yeah.

##### **Wozeparrot** [[00:28:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1727)]
But yeah, I'll get that by the end of tomorrow.

##### **Geohot** [[00:28:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1730)]
All right. Sounds good. Okay, yeah. Send it tomorrow. We just need a full plan to know whether this is going to be doable or not.

##### **Geohot** [[00:29:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1742)]
OK. Why is HCQ not deleted yet?

##### **Nimlgen** [[00:29:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1750)]
Yeah. I merged it into benchmarks, and all these failures in benchmark are because of HCQ2, so I'm just debugging this.

##### **Geohot** [[00:29:27](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1767)]
Yeah.

##### **Nimlgen** [[00:29:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1775)]
So, you know, I also merged copy staging, like the copy-kernel stuff.

##### **Geohot** [[00:29:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1787)]
The copy kernel stuff?

##### **Nimlgen** [[00:29:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1789)]
Yeah, with HCQ2. That's actually needed for the CPU to finish the migration to HCQ2, because the CPU doesn't have a copy queue, so it will use kernels to copy.

##### **Geohot** [[00:30:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1810)]
Oh, yeah. I see what you're doing. Yeah. I mean, this is kind of like, we don't really have to, like, put that back.

##### **Geohot** [[00:30:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1817)]
What if we just don't run the thing that, it's fine for now, but we could also just, like, not run the thing that creates copies.

##### **Nimlgen** [[00:30:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1828)]
What do you mean?

##### **Geohot** [[00:30:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1830)]
So that COPY, that CALL on COPY, is being created by a pass.

##### **Geohot** [[00:30:43](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1843)]
Yeah, create COPY. So what if we just didn't run that pass?

##### **Geohot** [[00:30:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1855)]
Yeah, pm_copy_from_store.

##### **Geohot** [[00:31:06](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1866)]
I see. I mean, we could just not run that pass if we don't have an SDMA engine.

##### **Geohot** [[00:31:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1878)]
That's a better way to do it.

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1881)]
I don't know. This is fine for now. Do you think we could have HCQ deleted by the end of this sprint?

##### **Nimlgen** [[00:31:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1890)]
Yeah. So we actually have a PR already to enable it by default in CI. I have several tests failing; I'm just going to fix them today or tomorrow. There aren't many, and they're all multi-tensor tests. I'm fixing the stability. I also fixed the BEAM problem with HCQ2.

##### **Nimlgen** [[00:31:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1915)]
LLMs are still slower than they were before because of the CPU enqueue time, which should also be fixed once the CPU fully becomes HCQ2.

##### **Nimlgen** [[00:32:14](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1934)]
I mean, basically, for CPU right now we still use the old Program stuff, always called in the HCQ1 style. The idea is to do the same as for AMD: build the binary blob with the function addresses and just execute that in the runners.

##### **Nimlgen** [[00:32:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1965)]
So that's already possible. And after that, HCQ2... I mean...

##### **Nimlgen** [[00:32:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1975)]
I don't know how I want to design that, but right now the reason HCQ2 enqueue is slower is that we have a lot of C kernels that are submitted from Python.

##### **Nimlgen** [[00:33:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=1993)]
And, I mean, potentially, after we generate all the C kernels to submit to AMD, we can just run HCQ2 again on these C kernels, and we're going to have only one call.

##### **Geohot** [[00:33:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2012)]
Yeah, that's cool. That makes sense. You could totally schedule your kernels. I like that recursive approach: first you schedule an AMD kernel, which gives you a whole bunch of scheduling C kernels. Then you run HCQ2 again to schedule all those, basically put them in a graph, and you're left with one C call. That's great.

##### **Geohot** [[00:33:59](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2039)]
Yeah.

##### **Geohot** [[00:34:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2042)]
Yeah.

##### **Nimlgen** [[00:34:04](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2044)]
Also, I think I'm going to break the HCQ1 CPU stuff for now. If someone is using offloading, that's going to be slow.

##### **Geohot** [[00:34:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2058)]
Using offloading?

##### **Geohot** [[00:34:21](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2061)]
Oh yeah, that's fine. If you just mean optimizer offloading, that doesn't matter, as long as it doesn't make Comma's USB stuff slow.

##### **Geohot** [[00:34:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2069)]
Yeah.

##### **Geohot** [[00:34:31](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2071)]
Yeah, no, that's totally fine. We can delete that. It would be great if we could delete HCQ by the end of this sprint and be back down below 25,000 lines.

##### **Geohot** [[00:34:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2087)]
Yeah. And I will look into that network card for you. I plugged the wires in, and the wires say Mellanox on them. This probably doesn't matter, but I don't know, maybe Broadcom needs different wires. I'll buy new wires. They're just plugged into the switch.

##### **Nimlgen** [[00:35:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2111)]
Yeah. I haven't looked much into that. I've just been asking GPT, and it's not really happy with the card on R5.

##### **Nimlgen** [[00:35:24](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2124)]
For some reason, ethtool reports that the RoCE capability is off on it.

##### **Nimlgen** [[00:35:43](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2143)]
And actually, the driver also doesn't enable...

##### **Geohot** [[00:35:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2155)]
Yeah, this is my job. I will get the machines pinging each other. You shouldn't have to worry about this. Let's just get HCQ deleted this sprint and then next sprint focus on multi-machine training.

##### **Geohot** [[00:36:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2171)]
Potentially that multi-compute-queue stuff. Did you follow that at all, what it is in AMD hardware?

##### **Nimlgen** [[00:36:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2179)]
Yeah. Multiple compute queues should actually already work with HCQ2.

##### **Geohot** [[00:36:27](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2187)]
Yeah.

##### **Geohot** [[00:36:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2189)]
Yeah, it shouldn't be a big deviation. I mean, basically, we just need to have two queues and some primitive to synchronize between them. I've been working on open-source MEC replacements. Do you know if there's a way... Do we actually need two queues?

##### **Geohot** [[00:36:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2207)]
Is there a way to launch a kernel and then not synchronize that kernel and launch another kernel right after it?

##### **Geohot** [[00:36:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2216)]
Yeah.

##### **Geohot** [[00:36:58](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2218)]
You know what I mean? It could actually be one queue.

##### **Nimlgen** [[00:37:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2222)]
Yeah, but actually, I don't know.

##### **Nimlgen** [[00:37:05](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2225)]
Yeah, it's possible to do that, but there is a kind of barrier you should place between two executions to make them dependent, to make them wait for each other. I mean, there is only a barrier: you can't wait for the first or the second; you can just put a barrier and wait for both.

##### **Geohot** [[00:37:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2252)]
Yeah, that makes sense. I mean, where I see us going, I think by the end of this year tinygrad is going to be caught up with the rest of the world. We're going to have basically state-of-the-art kernels matching the current TileLang/Torch paradigm.

##### **Geohot** [[00:37:52](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2272)]
I think most of next year is going to be focused on megakernels. And then like, kind of what megakernels are.

##### **Geohot** [[00:38:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2281)]
So yeah, this is why HCQ2 is so important: what does it really mean to have two kernels? Well, the kernel aspect means several things, right? There's a call aspect to it, but there's also a barrier aspect to it. And these things are completely different.

##### **Geohot** [[00:38:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2305)]
Yeah. I think where we're really going to start to see gains over everybody else is once we can go below the API layer and start to pry apart these concepts. Right now, if I'm in HIP and I have a single queue, and I launch a kernel and then a second kernel, HIP is going to promise me that the first kernel entirely completes before it launches the second kernel, right?

##### **Nimlgen** [[00:38:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2335)]
Yeah. I mean, you can use streams.

##### **Geohot** [[00:39:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2341)]
Well, I could use two queues and put the kernels on two queues, right? What do you mean by streams?

##### **Nimlgen** [[00:39:07](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2347)]
That's actually the same thing.

##### **Geohot** [[00:39:09](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2349)]
Oh, streams are just... Okay. Yeah.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2353)]
But yeah, I mean, the distinction there is that it's a lot easier to think about things when they're all single-threaded and you don't have to deal with synchronization. The synchronization is just kind of implicit.

##### **Geohot** [[00:39:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2375)]
Yeah. Have you looked into how other people are doing megakernels?

##### **Nimlgen** [[00:39:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2384)]
Not much, but yeah.

##### **Geohot** [[00:39:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2387)]
I mean, eventually, I think what we're doing next year mostly is going to be something kind of like writing an operating system.

##### **Geohot** [[00:39:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2393)]
And I want this operating system to be universal. I want this operating system to work on GPUs and CPUs and support the kinds of primitives that we need.

##### **Geohot** [[00:40:05](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2405)]
Imagine instead of using all the GPU's dispatch logic, we just have 256 long-running kernels.

##### **Geohot** [[00:40:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2417)]
And these kernels, like, parse the queue themselves.

##### **Nimlgen** [[00:40:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2435)]
I mean, ops_cpu is kind of the same thing, and I think the only primitives we might be missing are atomic operations. The CPU is really close to a megakernel, in some way.

##### **Geohot** [[00:40:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2449)]
I'm not exactly sure how the CPU one works, but what I think the CPU one is, is you're taking a global dimension and making it threads, and then you're putting a loop in each one of those threads.

##### **Geohot** [[00:41:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2462)]
And you don't exactly want to do that, but you do want to do this, because the different CUs, or the different threads, may run different numbers of pieces of compute.

##### **Geohot** [[00:41:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2477)]
See what I mean by that? Yeah. Yeah. Does the CPU one support that now?

##### **Nimlgen** [[00:41:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2485)]
Yeah, it won't support that.

##### **Geohot** [[00:41:27](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2487)]
It won't support that, yeah. I mean, that's just, look, it's not for right now, but it's what we kind of have to think about, right? We don't want to pre-decide where every piece of compute is going to run, because you can't calculate how the cache hits are going to go and stuff.

##### **Geohot** [[00:41:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2504)]
We want the GPU itself to... And this is all going to depend on what the latency of atomics is, or how well we can synchronize these things, but I suspect that we can build runtimes that can effectively run the same queue. Again, this is why it's so important that we want to move to HCQ2, where we can look at what these queues are. We can run the same queue in a way that lets us do much more fine-grained overlapping.

##### **Geohot** [[00:42:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2533)]
Yeah.

##### **Geohot** [[00:42:15](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2535)]
But yeah, no, I mean, I think a lot of the projects next year are going to look like: how can we best synchronize between CUs?

##### **Geohot** [[00:42:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2548)]
Because I remember the experiments with synchronizing between the XCDs using atomics were a lot slower than whatever MEC was doing.

##### **Geohot** [[00:42:41](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2561)]
Yeah, like why we needed all that AQL stuff. But with the open-source MEC, we're finally going to get to see what MEC is doing.

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2573)]
All right.

##### **Geohot** [[00:42:57](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2577)]
Yeah, I'm excited to understand that. But cool. All right, great. HCQ gone this sprint?

##### **Nimlgen** [[00:43:06](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2586)]
Yeah. Also, I forgot to mention: HCQ2 now has proper profiling. So in VIZ=2...

##### **Geohot** [[00:43:19](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2599)]
With VIZ=2, so the SQTT stuff works?

##### **Nimlgen** [[00:43:23](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2603)]
Not SQTT, but SQTT is kind of easy to port. All the timings are now fixed and work fine.

##### **Geohot** [[00:43:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2615)]
All right. Let's test that: HCQ2=1 VIZ=1 python test/test_tiny.py TestTiny.test_gemm.

##### **Geohot** [[00:43:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2630)]
Does HCQ2 take longer to start up?

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2633)]
Oh, I did VIZ=2.

##### **Geohot** [[00:43:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2636)]
Oh, no, that's going to break my computer.

##### **Geohot** [[00:44:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2641)]
So HCQ... I mean...

##### **Nimlgen** [[00:44:06](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2646)]
Yeah, it takes... What do you mean, longer to start up? The schedule passes take, I think, about 50% longer on average.

##### **Geohot** [[00:44:20](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2660)]
Occupied. Why is that occupied? Use PORT= to change? Oh my... Oh.

##### **Geohot** [[00:44:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2675)]
Yeah, I feel like every once in a while, it's just, like, really slow.

##### **Geohot** [[00:44:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2687)]
What's it doing?

##### **Geohot** [[00:44:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2696)]
That was fast. Okay, cool. Oh, nice. Yeah, I see all the HCQ compile-kernel stuff.

##### **Geohot** [[00:45:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2717)]
Nice. So that's what you mean by it works on the profiler. That's great.

##### **Geohot** [[00:45:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2728)]
Sweet. The more we can reuse the same abstractions, the better. I really like the double-HCQ thing.

##### **Geohot** [[00:45:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2742)]
Anything else?

##### **Nimlgen** [[00:45:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2745)]
No.

##### **Geohot** [[00:45:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2750)]
All right. On to mine: why is rangeify still long and confusing?

##### **Geohot** [[00:45:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2755)]
So I didn't get to work on it too much last sprint. I worked on all the stuff needed for fast Qwen3.6.

##### **Geohot** [[00:46:06](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2766)]
I did that custom-kernel CONTIGUOUS thing. I did the prototype of it.

##### **Geohot** [[00:46:14](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2774)]
Yeah. So we have state-of-the-art Qwen3.6 on AMD. It's not quite merged yet, but it should be merged this sprint. I've been slowly chipping away at all the little pieces of it. It uses a bunch of custom kernels, but I think this idea of having custom kernels and then working to remove them, to make our codegen good enough to generate them, is the right idea. The main custom kernels are Flash Attention, because we don't have PCONTIG; Gated DeltaNet, because we don't have SCAN; and a bunch of linear kernels because BEAM isn't finding WMMA.

##### **Geohot** [[00:47:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2831)]
The decode kernels BEAM finds really fast for the GGUF-packed stuff. But the prefill kernels it doesn't, because it doesn't use WMMA for some reason.

##### **Geohot** [[00:47:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2845)]
So that's probably fixable with the UNSHARD stuff.

##### **Geohot** [[00:47:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2848)]
Yeah, but it's basically just those three things that prevent tinygrad from beating the state of the art.

##### **Geohot** [[00:47:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2858)]
And it's 3090 state of the art, too. It's not far off from being state of the art on Qwen3.6.

##### **Geohot** [[00:47:48](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2868)]
It's those three things.

##### **Geohot** [[00:47:51](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2871)]
So yeah, this sprint I'm going to work mostly on rangeify fixes.

##### **Geohot** [[00:47:57](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2877)]
There are a bunch of hacks to deal with the custom-kernel thing. It's better that we don't put CONTIGUOUS in the user graph, but now CONTIGUOUS is being added by this realization pass, which happens pretty early. We shouldn't have to do that. We'll have a pass later on in rangeify. We have to stop saying that there's going to be one magical place where we decide where all the buffers are going to be.

##### **Geohot** [[00:48:26](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2906)]
So the new rangeify is going to basically insert too many buffers, in almost every place you could want a buffer.

##### **Geohot** [[00:48:33](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2913)]
And then figure out which ones it can remove, and which ones are required because of things like custom kernels. We can do all of that really late. So if anything cancels out... Right now we may still be thinking about the fact that sometimes you have to reshape for a custom kernel, and movement ops should be long gone by this point.

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2936)]
We have one pass very early on to remove all the movement ops. Once we're in the rangeify world, we can do a lot of kernel optimizations directly on that stuff without ever having to think about a movement op.

##### **Geohot** [[00:49:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2953)]
That's good.

##### **Geohot** [[00:49:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2957)]
I got Kimi running. Well, Codex got Kimi running. So we're getting eight tokens per second with Kimi in tinygrad. If we could get 10x more, that would be kind of nice. But that was with just tinygrad's kernels, not with AITER kernels.

##### **Geohot** [[00:49:36](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2976)]
But I think that to really get this high performance, this is a place where I think tinygrad can be competitive.

##### **Geohot** [[00:49:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=2989)]
If you saw these ultra-high-interactivity things, like TileRT...

##### **Geohot** [[00:50:03](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3003)]
Because I think that's a place where we can be competitive, and a place where some people would be really interested.

##### **Geohot** [[00:50:13](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3013)]
I don't know. I think about what an advantage I would have had. I went to DEF CON this weekend, and I would have had such an advantage in the CTF if I had 500-token-per-second Kimi. Most people don't even know how great Kimi is. Most people are struggling to get Codex not to refuse security stuff. Kimi doesn't do that. But yeah, 500-token-per-second Kimi gives you a real advantage in a lot of competitive environments. So I think this is going to be the thing next year, if we really are at a place where LLMs are kind of good enough.

##### **Geohot** [[00:50:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3050)]
Which they kind of are. They can always be smarter, but...

##### **Geohot** [[00:50:56](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3056)]
You know, there are two axes to this: smarter and faster.

##### **Geohot** [[00:51:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3061)]
Fundamentally, everyone's moving toward this way of thinking. It's not a question of how smart your LLM is; it's a question of how often it completes the task and how quickly it completes the task. That's all that matters. I'm not going to build smarter LLMs, but we can build quicker LLMs, so I think that's a good thing to focus on. Cool. How close are we to merging RDNA3 assembly?

##### **Raine** [[00:51:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3089)]
Yeah. I spent the last week getting the last few tests passing. We're down to six tests for the entire CI suite.

##### **Raine** [[00:51:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3098)]
I simplified it a lot. We're under 600 lines of code for the entire backend file, which I'm pretty happy about. Now I'm basically trying to make it not generate slop. Even if you look at some of the GEMM kernels versus LLVM, there are a lot of unnecessary UOps. I found a problem where the linearizer wasn't assigning the proper priority to loads and stores because they're already Ops. So it wasn't batching memory ops together or placing them early and late.

##### **Raine** [[00:52:09](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3129)]
So just today I've started working on making the code actually good and looking at performance. I increased GEMM performance by about 10% just this morning. There's a lot of room for improvement there.

##### **Raine** [[00:52:20](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3140)]
One problem I'm having is that I don't understand why the CI tests are taking so long compared to the LLVM backend. Every time I push to my PR branch, it runs for about 15 minutes and then just cancels.

##### **Raine** [[00:52:36](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3156)]
Locally, it's about a 10% difference in runtime versus LLVM. I don't think this is inherent to ISA backends, because x86 is pretty close to the other compilers. Here, I can post that.

##### **Geohot** [[00:52:49](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3169)]
I see your test being slow. I mean...

##### **Raine** [[00:52:55](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3175)]
Yeah, it's probably just slow. I run it locally and it's like 60 versus 70 seconds, and then here it's three times as long. Is it something about the runner environment?

##### **Chrism** [[00:53:04](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3184)]
When you run it locally, are you running with CACHELEVEL=0, or are you running with a cache?

##### **Raine** [[00:53:10](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3190)]
I don't specify. Oh, well, that's what it is. Okay.

##### **Geohot** [[00:53:15](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3195)]
Yeah. So you're having to compile all the instructions with the compiler. Run with CACHELEVEL=0, because that's effectively what you're getting in CI.

##### **Geohot** [[00:53:27](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3207)]
Yeah, well, it's got to compile everything, right?

##### **Raine** [[00:53:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3209)]
Yeah, yeah, yeah. So that's kind of annoying.

##### **Geohot** [[00:53:33](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3213)]
Run one test with VIZ and look at what it's doing. Then run it with CACHELEVEL=0, and you'll see how much slower it is. But yeah, that's probably what that is. I also see a ton of changes to a ton of different files here. Are there any small things to merge first?

##### **Raine** [[00:53:51](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3231)]
I don't think so. Most of them are specific to this backend, I think. There are very small changes...

##### **Geohot** [[00:54:02](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3242)]
No, I mean, look at your change to LLVM IR, right? You have this...

##### **Raine** [[00:54:09](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3249)]
I moved the WMMA pattern matchers to opt, right? Just so I didn't have to duplicate them in my backend.

##### **Geohot** [[00:54:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3257)]
That's the kind of thing that can get merged as its own PR.

##### **Raine** [[00:54:20](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3260)]
Okay.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3261)]
I also see little things like UOp.group, where you're adding the kwargs, right? That stuff can be merged.

##### **Geohot** [[00:54:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3268)]
to_storage_scalar.

##### **Geohot** [[00:54:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3272)]
I don't know how I feel about an invalid type returning x and not throwing an exception.

##### **Raine** [[00:54:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3278)]
Yeah, that was a bit of a hack. Sorry.

##### **Geohot** [[00:54:41](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3281)]
I mean, why does it even need that? Shouldn't it just return x already?

##### **Raine** [[00:54:46](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3286)]
I don't know. No, that was causing a problem. I probably could have found a better way to fix that. Maybe there was something wrong in the backend. That was for bfloat16 stuff.

##### **Geohot** [[00:54:57](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3297)]
And then I see huge diffs to these ins.py files too.

##### **Raine** [[00:55:01](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3301)]
Because I had to regenerate it. I had to declare a class so that, if I use it as an arg, it is hashable or can compare against itself. So I created a class to wrap the instructions so that it doesn't throw an error.

##### **Geohot** [[00:55:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3318)]
Create a class?

##### **Raine** [[00:55:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3318)]
So all of them... If you go to the DSL, it's an Ops.INS. It just wraps the...

##### **Geohot** [[00:55:25](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3325)]
I see what it's doing. I don't exactly understand why you need that.

##### **Raine** [[00:55:30](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3330)]
Otherwise I get an error that it can't compare the arguments when it tuplizes them, I think.

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3336)]
Yeah. I wouldn't fix it like that. Okay.

##### **Raine** [[00:55:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3342)]
It throws an error because they're functools.partial objects, and it doesn't like that.

##### **Geohot** [[00:55:47](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3347)]
Yeah, I get that.

##### **Geohot** [[00:55:51](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3351)]
This should be thought about in a different way, right? The fundamental problem you want to solve here is not, "Why can't I compare tuples?" It's, "Why am I comparing instructions?"

##### **Raine** [[00:56:06](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3366)]
Okay. But we pass them as args.

##### **Geohot** [[00:56:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3371)]
That's not the problem. This is related to your load ordering issue too. Okay.

##### **Geohot** [[00:56:18](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3378)]
You know what I mean? Do you know where that comparison happens?

##### **Raine** [[00:56:22](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3382)]
No. Is that in linearize? Oh, okay. So the linearizer...

##### **Geohot** [[00:56:29](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3389)]
The right solution here is not to add some class so you can compare them. It's to ask, "What do I actually want the sort order to be?"

##### **Raine** [[00:56:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3398)]
Okay, yeah. So why am I comparing them in linearize?

##### **Geohot** [[00:56:42](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3402)]
Also, the linearize comparison will short-circuit if it compares differently with something earlier in the tuple.

##### **Raine** [[00:56:53](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3413)]
Yeah. So maybe I could add something to... Yeah, I could just check if it's a functools.partial or an instruction, and then it would just fail there, or compare there.

##### **Geohot** [[00:57:04](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3424)]
Yeah, you could potentially do that.

##### **Geohot** [[00:57:07](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3427)]
But think about what you want, because that sort order is not obvious.

##### **Raine** [[00:57:11](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3431)]
Yeah.

##### **Geohot** [[00:57:12](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3432)]
And the solution is not to hack something to make it pass. The solution is to think about what you want in the sort order.

##### **Raine** [[00:57:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3437)]
Cool. So what are your thoughts on a good benchmark for when it's mergeable, performance-wise? Like if I'm looking at GEMM and tensor cores.

##### **Geohot** [[00:57:26](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3446)]
I would run whole models. Once your whole models are within 30% of LLVM, you're good. Maybe even within 2x.

##### **Geohot** [[00:57:46](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3466)]
It shouldn't be more than 2x. If it's more than 2x, you're doing something pretty wrong. I don't care about things like LLVM's heuristics for cycles, how many cycles an instruction takes, and reordering: micro-optimizations like that. But if you're off by more than 2x, it's probably because you're not doing memory correctly. I want it doing memory correctly, because that's pretty fundamental to how the thing works.

##### **Geohot** [[00:58:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3497)]
Okay. 2x for MNIST Trainer, but not just MNIST Trainer: MNIST Trainer, ResNet, LLaMA, everything within 2x. Yeah, you can be 2x slower.

##### **Raine** [[00:58:32](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3512)]
Sounds good.

##### **Geohot** [[00:58:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3515)]
Yeah. 2x is a good number for that. It's worth getting this merged, and then we can figure out which optimizations we're not doing.

##### **Geohot** [[00:58:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3525)]
Great.

##### **Geohot** [[00:58:50](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3530)]
Okay. Yeah. I think that's pretty much the meeting.

##### **Geohot** [[00:58:58](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3538)]
You can see where this is all going. It all takes a long time, and I probably say this in a lot of meetings. But where we're eventually going with this is: we have these very fast AITER kernels, and we can slowly back them out. Can we run the register allocator?

##### **Geohot** [[00:59:16](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3556)]
Can we rewrite the AITER kernels not to have any register numbers, and then run the register allocator on them?

##### **Geohot** [[00:59:22](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3562)]
Can we then put them in a graph and not in a LINEAR? Can the linearizer recover that structure? Then can we not do instruction selection? Can we back out instruction selection and go to tinygrad Ops?

##### **Geohot** [[00:59:34](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3574)]
Then can we go to higher-level tinygrad Ops? Can we remove the WMMAs and stuff, and have BEAM automatically find them? All that instruction-selection stuff should be good.

##### **Geohot** [[00:59:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3585)]
And now we're starting to get to rangeify, right? Can we back out beyond rangeify? Can we write this just in terms of something that looks like AMD copy matmul? Then we go up even higher and say, okay, can we just write this in terms of Tensor A and B, and have that generate a fast GEMM that matches AITER? So we can do this slowly, one step at a time. It's very important that we do things methodically, and that we have CI and testing working well, because that's our advantage over everybody else. You see all these people... Look at that TileRT thing. It's cool; smart people are doing it. But start to look into how those microkernels are actually working, and...

##### **Geohot** [[01:00:28](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3628)]
You know, it's very, very specific to NVIDIA and to...

##### **Geohot** [[01:00:38](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3638)]
Let me find the file I was looking at.

##### **Geohot** [[01:00:44](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3644)]
You see how they have directories for each model, and then for each model they have...

##### **Geohot** [[01:00:57](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3657)]
Here are your temp vars. There shouldn't be something called temp vars. That should be automatically scheduled.

##### **Geohot** [[01:01:17](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3677)]
But yeah, this is actually cool to read. This is kind of better than I thought. This is pretty good.

##### **Geohot** [[01:01:24](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3684)]
The TileLang people are ahead of us. We're nipping at the heels of the TileLang people.

##### **Geohot** [[01:01:35](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3695)]
I don't actually totally understand this.

##### **Geohot** [[01:01:45](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3705)]
Interesting. They're registering these micro-ops. But yeah, fun thing to read. This is not where we want to go. We don't want to have to think about micro-ops. We want to think about how our entire compiler can target MEC, our runtime, the Tenstorrent runtime, CPUs, and everything.

##### **Geohot** [[01:02:08](https://www.youtube.com/watch?v=MbgtBg3gKSU&t=3728)]
So I think that's where this eventually goes. Cool. That's the meeting. Thanks, everyone.
