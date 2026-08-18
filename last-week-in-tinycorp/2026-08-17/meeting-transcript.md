# 2026-08-17 Meeting

### Meeting Agenda

**Time:** new meeting #33, 8/17 9am Monday San Diego time
- company update
- HCQ2
- GPT-OSS
- LLaMA training, MXFP4
- rangeify, LLM
- CONST weak dtype
- SLICE, comma big model
- bounties, RDNA3, comma happiness, Kimi


### Audio

[Youtube Link](https://www.youtube.com/watch?v=YtVlJ4tgJco)

### Highlights

* **[Company Update](#geohot-000000)**: tinygrad’s Chestnut launch was a success, with 397 units sold; the ready-to-drive edition with a 9060 was the most popular, and AMD also sent two MI350P cards for testing. 
* **[CI Stability](#geohot-000097)**: HCQ2 caused CI instability that had to be reverted because it made work difficult for the rest of the company; the team plans to move away from GitHub, especially after GitHub itself went down. 
* **[HCQ2 Performance](#nimlgen-000187)**: HCQ2 is back in CI after two race conditions were fixed, while CPU is now fully HCQ2 with a unified CPU program across backends; Qwen remains a major performance gap to investigate. 
* **[Benchmark Tracking](#geohot-000507)**: benchmark execution has become unusually slow, prompting a plan to track benchmark duration in TinyStats alongside CI stability so regressions can be identified rather than discovered ad hoc. 
* **[GPT-OSS Performance](#wozeparrot-000645)**: GPT-OSS reached about 1.2 seconds per step after switching from ZeRO-1 to ZeRO-2 and sharding gradients, with a Flash Attention sliding-window fix also eliminating recomputation; the run is around 4.5 hours total. 
* **[CI/CD Infrastructure](#wozeparrot-000753)**: tiny-infra is being moved into CI/CD so pushes automatically deploy through an Actions runner; the team is also considering Gitea because of GitHub’s outage and Gitea’s much faster performance. 
* **[LLaMA Performance](#qazalin-000937)**: the latest LLaMA run reached 130 minutes versus AMD’s 127 minutes, with custom BF16 GEMM and Flash Attention assembly closing the remaining gap; a faster and correct backward assembly could bring tinygrad to parity. 
* **[Memory & Communication](#geohot-001162)**: the memory planner can free communication buffers before SDMA finishes; Geohot argues tinygrad should ultimately separate where a kernel executes from where its memory resides, treating SDMA as another execution engine. 
* **[Rangeify Rewrite](#geohot-001786)**: the new rangeify removes `BIND` special cases by treating variables like ordinary buffers, while `CONTIGUOUS` stays in rangeify and `STAGE` becomes the explicit mechanism for creating buffers and ending ranges. 
* **[Custom MEC](#geohot-002140)**: a fully working custom MEC now exposes the GPU’s actual dispatch machinery and points toward an OS design using roughly 96 long-running kernels instead of traditional GPU dispatch; future hardware could use independent cores with local communication primitives. 
* **[Weak CONST Dtypes](#chenyu-002301)**: Chenyu’s large PR makes every `CONST` weakly typed before dtype decomposition and removes strong-dtype constants, exposing and cleaning up older code that had relied on `CONST` carrying a dtype. 
* **[SLICE Removal](#chrism-002736)**: `SLICE` is gone; variable offsets remain unfinished, but variables now being more like buffers may make offset support easier and could help eliminate sub-buffers across CL and WebGPU. 
* **[CI Performance](#chrism-002825)**: Gitea CI is improving, but HCQ2 is still failing with an apparent OOM; the team is investigating memory behavior, compile-server infrastructure, and Docker/Cloudflare caching to make CI more reliable and efficient. 
* **[RDNA3 Backend](#raine-003442)**: RDNA3 now runs MNIST and LLaMA with compile times and multiple tests fixed, leaving FP16 GEMM as the major failure; Geohot wants the backend merged rather than adding a specialized WMMA scheduler, preferring a future general solution that jointly handles register allocation and linearization. 
* **[Release Timing](#chenyu-004210)**: the team will delay the release until CI and benchmarks are stable and reliable, unless a new release becomes necessary to help a Chestnut customer. 


### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=0)]
As far as the company update: we launched the Chestnut.

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=7)]
Pretty big success. We sold 397 of them.

##### **Geohot** [[00:00:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=14)]
So yeah, it was pretty much exactly what we forecasted. We sold more ready-to-drives than expected. Most people bought the ready-to-drive edition, which is the edition that includes a 9060.

##### **Geohot** [[00:00:32](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=32)]
I drove up to San Francisco and back this weekend on an eGPU. One minor model lag, but otherwise totally stable. The model lag was just that I couldn't engage for 10 seconds, so it seems to be working pretty well.

##### **Geohot** [[00:00:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=52)]
AMD sent us two MI350P cards to play with. Hopefully we'll get those put into a computer today.

##### **Geohot** [[00:01:01](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=61)]
MI350P is half an MI350X. It's a pretty nice little PCIe card.

##### **Geohot** [[00:01:12](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=72)]
Yeah, sure. That sounds right. So yeah, MI350Ps.

##### **Geohot** [[00:01:23](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=83)]
We need to talk about CI stability. I reverted HCQ2. We can't have this. But it's harder to rail about CI stability when GitHub is down.

##### **Geohot** [[00:01:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=97)]
You just kind of can't believe it. So yeah, we're going to move off GitHub. But there was CI instability caused by HCQ2, and we can't have that because it makes it really hard for everybody else in the company to work. That's pretty much it. Chestnut launch was a success, so we can expect more noobs in the Discord complaining about their Chestnut not working.

##### **Chenyu** [[00:02:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=134)]
Oh, we have a channel for that?

##### **Geohot** [[00:02:18](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=138)]
GPU USB. GPU on USB. That's not Chestnut.

##### **Chenyu** [[00:02:23](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=143)]
I think people will probably complain to comma.

##### **Geohot** [[00:02:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=146)]
If I connect a NIC to the Chestnut, it should fall back to PCIe, right? I don't know. It's not supported. Yeah.

##### **Chenyu** [[00:02:39](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=159)]
Okay, we'll see. I think we'll report to comma if we're not happy.

##### **Geohot** [[00:02:46](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=166)]
Yeah, yeah. Well, I mean, the firmware, we're kind of the ones maintaining it, but...

##### **Chenyu** [[00:02:55](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=175)]
Oh, sounds good. Okay, let's move on. We can start with HCQ2.

##### **Nimlgen** [[00:03:07](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=187)]
Yeah. So, related to the CI, HCQ2 has been back in CI for a couple of days, and I fixed the two races, so it should be stable now.

##### **Nimlgen** [[00:03:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=206)]
Also, CPU is fully HCQ2 now; that merged today. We just send one CPU program for all HCQ kernels, across different backends, no matter what.

##### **Geohot** [[00:03:48](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=228)]
Yeah, I see a big boost to tokens per second.

##### **Nimlgen** [[00:03:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=232)]
Yeah, and I have another patch too, once GitHub is fixed.

##### **Geohot** [[00:04:01](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=241)]
I mean, it's not back to where it was yet.

##### **Nimlgen** [[00:04:09](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=249)]
I have another one to make it a bit better.

##### **Geohot** [[00:04:18](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=258)]
Yeah. If you look at that Qwen MoE on the right there, we want to get that back to where it was. You can really see it if you zoom out one more. I think that's probably the one to watch.

##### **Nimlgen** [[00:04:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=277)]
Yeah. So it was 150. It's 100 right now in master, and I have a patch to make it 120. I'm looking into that.

##### **Chenyu** [[00:04:50](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=290)]
Yeah. Why is it not 160?

##### **Geohot** [[00:04:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=292)]
How did it... Why is it not 160? Why is it so much slower?

##### **Nimlgen** [[00:04:59](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=299)]
I'll look into that. The main speedup was that we had uncacheable programs, so that was the performance issue. The other issue was Python time.

##### **Geohot** [[00:05:21](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=321)]
There shouldn't be too much Python time unless we're doing something pretty bad. That should be in a JIT entirely.

##### **Nimlgen** [[00:05:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=336)]
I'll look into Qwen. I just have CIFAR matching HCQ1 speed, right? So Qwen is the next one for me to look into.

##### **Geohot** [[00:05:50](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=350)]
Yeah. I mean, CIFAR, I don't see much of a difference at all. Oh, I guess the CIFAR six-GPU one. Is that what you're talking about?

##### **Nimlgen** [[00:06:03](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=363)]
Yeah, that one. It's not in master. I have a pull request; I'm just waiting for GitHub.

##### **Geohot** [[00:06:11](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=371)]
Oh, I got it. Cool. The instability is much worse than a bit of a slowdown.

##### **Chenyu** [[00:06:18](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=378)]
Also, the time to run benchmarks is very slow. BEAM is slow, but MLPerf training, ResNet on six GPUs, is also pretty slow, as in 10 to 15 minutes. Do we know what's happening?

##### **Nimlgen** [[00:06:48](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=408)]
Yeah, I'll look into that. Something degraded, because the first step was faster than it is right now.

##### **Chenyu** [[00:07:04](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=424)]
Just focus on whether it's HCQ2-related. I also tried Metal BEAMing OLMoE, and it's very slow. I think half of that time is something with symbolic being slow, so that's not really HCQ2-related. I was tempted to reduce JITBEAM to one or something; otherwise this takes forever.

##### **Geohot** [[00:07:30](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=450)]
People were just saying BEAM in general is having issues.

##### **Chenyu** [[00:07:34](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=454)]
I can't believe that. I mean, maybe not issues, but it's just very slow.

##### **Geohot** [[00:07:40](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=460)]
Yeah. BEAM is some of the oldest code in tinygrad. We have to rewrite it in a new style. I've been thinking about how it gets changed. It should pretty much be a graph rewrite. We also want to parallelize the lowering and compilation in general, I think.

##### **Chenyu** [[00:08:02](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=482)]
Yeah. Anyway, that would be nice. Otherwise, benchmarks are very slow.

##### **Geohot** [[00:08:10](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=490)]
Is it an HCQ2 regression, or is it just slow?

##### **Chenyu** [[00:08:15](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=495)]
I don't remember this being this slow a week ago. It might be that someone, including me, merged something we weren't aware of, and it all adds up.

##### **Geohot** [[00:08:27](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=507)]
Can we have this in TinyStats? Why don't we have how long benchmarks take in TinyStats?

##### **Chenyu** [[00:08:32](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=512)]
Yeah.

##### **Geohot** [[00:08:33](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=513)]
Great.

##### **Chenyu** [[00:08:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=517)]
Okay, sounds good. I want you to track benchmark time.

##### **Geohot** [[00:08:41](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=521)]
Because I'm going to track CI.

##### **Chenyu** [[00:08:47](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=527)]
Cool. Anything else for HCQ2?

##### **Nimlgen** [[00:08:51](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=531)]
Not for HCQ2, but we also have the Broadcom driver working. I'll clean it up. That's probably not my focus, though. This week I'm still focusing on HCQ1 removal. The remaining steps are USB for AMD, all the speed regressions, then NVIDIA and QCOM.

##### **Geohot** [[00:09:31](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=571)]
Oh yeah. Are those machines working well?

##### **Nimlgen** [[00:09:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=576)]
Yeah.

##### **Geohot** [[00:09:38](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=578)]
Great.

##### **Chenyu** [[00:09:44](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=584)]
Sounds good. Anything else?

##### **Nimlgen** [[00:09:48](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=588)]
No.

##### **Chenyu** [[00:09:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=592)]
Okay, moving on: GPT-OSS. I just saw a run that's like 1.2 seconds.

##### **Wozeparrot** [[00:10:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=600)]
Yeah, we're at 1.2, just above 1.2. The machine does slow down quite a bit. At the beginning of the run we're at about 1.18, and then it goes up to almost 1.22 by the end.

##### **Geohot** [[00:10:18](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=618)]
Is it the same as the LLaMA slowness?

##### **Wozeparrot** [[00:10:21](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=621)]
Same as the LLaMA slowness, from the throttling. But this puts us at four hours 30.

##### **Wozeparrot** [[00:10:30](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=630)]
Also, all the slowdown is right at the beginning.

##### **Chenyu** [[00:10:34](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=634)]
Yeah. Great.

##### **Geohot** [[00:10:38](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=638)]
Four hours 30. All right, cool. So how are we?

##### **Wozeparrot** [[00:10:42](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=642)]
This is 1.2.

##### **Geohot** [[00:10:44](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=644)]
We're already at 1.2? Oh, that's great.

##### **Wozeparrot** [[00:10:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=645)]
This is 1.2 from just switching from ZeRO-1 to ZeRO-2. The grads are also sharded now, and this saves a bunch of comms. The other change is the Flash Attention sliding-window fix, so we don't have to recompute.

##### **Chenyu** [[00:11:12](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=672)]
Why is the total time four and a half hours, only one hour shorter, when the step got almost twice as fast?

##### **Wozeparrot** [[00:11:24](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=684)]
The step dropped 400 milliseconds.

##### **Qazalin** [[00:11:32](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=692)]
Oh, I see. Okay. Yeah.

##### **Chenyu** [[00:11:41](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=701)]
And this is on master?

##### **Wozeparrot** [[00:11:43](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=703)]
Not yet. That's what I'm doing this week. There's a bunch of stuff to clean up and then merge into master.

##### **Geohot** [[00:11:56](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=716)]
Cool. Yeah, the time all checks out. It's a little bit slower. I'm seeing 248 minutes if you just multiply it out, so there's about 20 minutes of overhead.

##### **Chenyu** [[00:12:13](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=733)]
Yeah, the first steps take a while, but don't worry about that. We'll fix it. We can also always just pre-cache it.

##### **Geohot** [[00:12:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=746)]
Cool. It seems like we're on track for that. Keep it up. Let's get to 800.

##### **Wozeparrot** [[00:12:33](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=753)]
I guess I'll use this to talk about some infrastructure too, since I've been working on that as well. We should hopefully have CI/CD by this week, so infra will deploy automatically once you push.

##### **Geohot** [[00:12:47](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=767)]
Got it. So you're moving tiny-infra into CI.

##### **Wozeparrot** [[00:12:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=772)]
Yes. Basically, the gateway will have an Actions runner, and when you push, that runner will deploy.

##### **Geohot** [[00:12:59](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=779)]
Cool. Maybe you also want to move our infra to Gitea?

##### **Wozeparrot** [[00:13:05](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=785)]
Yeah, I was thinking about that too after GitHub was just down this morning.

##### **Geohot** [[00:13:10](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=790)]
Yeah. I think Gitea is... I mean, it's not great yet, and we still have to come up with a backup strategy for Gitea. But otherwise I like it. It's just so much faster. Go to git.tinygrad.win now and click around. It's unbelievable how slow GitHub is.

##### **Chrism** [[00:13:28](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=808)]
And the PRs do a dry-run deploy or something like that?

##### **Wozeparrot** [[00:13:35](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=815)]
Yeah, we can do that.

##### **Geohot** [[00:13:38](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=818)]
Yeah, that makes sense. I don't really know exactly what dry run does.

##### **Chrism** [[00:13:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=825)]
Something to make sure that you didn't screw something up.

##### **Chenyu** [[00:13:48](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=828)]
It'll show you the deployment action before you actually deploy.

##### **Wozeparrot** [[00:13:53](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=833)]
The main deploy script already does a dry run to make sure nothing's broken before deploying.

##### **Geohot** [[00:14:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=840)]
Cool. Great. Good work getting TinyR8 back. So for TinyR9, can we have something so it doesn't wipe itself?

##### **Wozeparrot** [[00:14:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=856)]
Yeah, I fixed that. The takeover script was missing a check to see if there was an OS on the drive.

##### **Geohot** [[00:14:23](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=863)]
Okay. Yeah, it wiped two hours of LLM progress, but not that big a deal.

##### **Wozeparrot** [[00:14:30](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=870)]
Yeah, that should be fixed now.

##### **Chenyu** [[00:14:34](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=874)]
Is the MoE plan in the GPT-OSS channel still accurate?

##### **Wozeparrot** [[00:14:42](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=882)]
Yeah.

##### **Geohot** [[00:14:43](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=883)]
It looks like ZeRO gave you more than you estimated.

##### **Wozeparrot** [[00:14:51](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=891)]
ZeRO gave me about what I expected from the estimate, because ZeRO isn't the full comms fix either.

##### **Chenyu** [[00:15:08](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=908)]
I see. You know better; I'm just curious how the forecast speedup compares to the actual speedup.

##### **Wozeparrot** [[00:15:17](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=917)]
Yeah, it's about what I expected.

##### **Chenyu** [[00:15:23](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=923)]
Cool. Great. Anything else? No? Okay, moving on to LLaMA.

##### **Qazalin** [[00:15:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=937)]
I'll share my latest run. It's 130 minutes, and AMD did it on our machine in 127, so we're three minutes off.

##### **Geohot** [[00:15:57](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=957)]
What's the purple run?

##### **Qazalin** [[00:16:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=960)]
The purple run is currently running. I think it should finish faster than this one. The blue line is assembly for BF16 GEMMs, and the purple line is forward Flash Attention in assembly. There's still a backward pass where they're faster than us. If I get a fast and correct backward assembly, I believe we should be on par.

##### **Geohot** [[00:16:30](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=990)]
What did AMD get? Two hours and seven minutes?

##### **Qazalin** [[00:16:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=997)]
Yeah, 127 minutes.

##### **Geohot** [[00:16:39](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=999)]
We're almost there. How much of this stuff is merged?

##### **Qazalin** [[00:16:44](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1004)]
I'm going to start merging the custom-kernel stuff. I also have a project to express all the all-reduce stuff.

##### **Geohot** [[00:16:55](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1015)]
I'm less worried about the custom assembly than I am about all the all-reduce complexity. Is this on HCQ1 or HCQ2?

##### **Qazalin** [[00:17:07](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1027)]
HCQ1.

##### **Geohot** [[00:17:11](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1031)]
Nimlgen, how close are we to HCQ2 being ready for this?

##### **Nimlgen** [[00:17:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1036)]
We just need all-to-all, like several SDMA queues.

##### **Geohot** [[00:17:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1042)]
Okay. I want to move the newest stuff to HCQ2. How is the communication represented on your branch now?

##### **Qazalin** [[00:17:44](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1064)]
There are sub-buffers in the all-reduce.

##### **Geohot** [[00:17:53](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1073)]
That's not too crazy unless there's some two-queue thing.

##### **Qazalin** [[00:18:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1080)]
It's the sub-buffers and the memory planner. There are subtleties now that `SLICE` is gone. You have a `SHRINK`, and I tag the UOp to say where it's coming from. I need a project for that.

##### **Geohot** [[00:18:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1116)]
The tag and the `SHRINK` should be fine; fix the planner. What about the asynchronicity and queues?

##### **Qazalin** [[00:18:59](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1139)]
The idles are the problem if we want to beat AMD.

##### **Geohot** [[00:19:07](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1147)]
What's the memory-planner bug?

##### **Qazalin** [[00:19:12](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1152)]
It frees the underlying buffers.

##### **Geohot** [[00:19:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1162)]
Right, the target of the communication can be freed before the communication is ready. The copies run on SDMA. Eventually tinygrad needs to represent where compute runs and which device has the memory as independent things. For example, memory can be on GPU 1 while a kernel runs on GPU 2. PCIe is slower than local memory, but tinygrad still has to express that. SDMA is no different from a compute engine except that it can't express ALUs.

##### **Geohot** [[00:20:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1226)]
Late in the pipeline, we can transform a kernel back into a `COPY`. Generalize it by separating where a kernel runs from the memory it accesses.

##### **Qazalin** [[00:20:55](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1255)]
The ultimate goal is not having SDMA.

##### **Geohot** [[00:21:03](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1263)]
Don't worry about that; it's harder and shouldn't matter. We just need to express whether something runs on SDMA or compute. Are the idles caused by an SDMA slowdown?

##### **Qazalin** [[00:21:38](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1298)]
The idles happen because the add kernel, an ALU that SDMA can't run, stalls waiting for SDMA. No other compute runs because there's one compute queue. I partially fixed that with the toposort.

##### **Geohot** [[00:22:06](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1326)]
It should all be handled by the toposort. Put the add after the next backward pass.

##### **Qazalin** [[00:22:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1334)]
Yeah, I'll focus on that.

##### **Geohot** [[00:22:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1345)]
What was AMD's MLPerf time?

##### **Qazalin** [[00:22:29](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1349)]
About 110 minutes.

##### **Geohot** [[00:22:31](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1351)]
Can we reach that on our crappy computers?

##### **Qazalin** [[00:22:35](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1355)]
No.

##### **Geohot** [[00:22:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1357)]
Why not? What's the breakdown?

##### **Qazalin** [[00:22:40](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1360)]
They get below one second per step. If I get Flash Attention to use their assembly, we should match. Right now it's only two or three minutes off.

##### **Geohot** [[00:23:04](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1384)]
This run looks even faster.

##### **Qazalin** [[00:23:08](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1388)]
It's not finished yet.

##### **Geohot** [[00:23:13](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1393)]
It's creeping upward.

##### **Qazalin** [[00:23:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1399)]
I'll share the link.

##### **Geohot** [[00:23:28](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1408)]
It's getting warmer in San Diego. That link doesn't work. Oh, I clicked the thing and now I see it.

##### **Qazalin** [[00:23:43](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1423)]
Interesting.

##### **Geohot** [[00:23:44](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1424)]
Weights & Biases is trying to make me pay. It keeps getting warmer.

##### **Qazalin** [[00:23:55](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1435)]
That could be it.

##### **Geohot** [[00:23:58](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1438)]
It was a perfect day.

##### **Chenyu** [[00:23:59](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1439)]
You need cold air in the office, like a data center.

##### **Geohot** [[00:24:06](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1446)]
We'll pump cold air in. Can we beat AMD's time?

##### **Qazalin** [[00:24:23](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1463)]
With our computers?

##### **Geohot** [[00:24:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1465)]
What's our best possible time?

##### **Qazalin** [[00:24:31](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1471)]
Once I finish moving and merging the assembly kernels, I can make the assembly and communication faster.

##### **Geohot** [[00:24:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1485)]
They copied the communication with four CUs, right?

##### **Qazalin** [[00:24:53](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1493)]
ROCm still stalls, but its stalls are half of ours, around 55 milliseconds.

##### **Geohot** [[00:25:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1514)]
Ours are around 100 milliseconds, so that's 1.1 seconds of pure compute.

##### **Qazalin** [[00:25:24](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1524)]
We're already around 1.1. With perfect communication, we can get below one second. By the way, did the cloud machine time out?

##### **Geohot** [[00:26:01](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1561)]
I backed it up. We wasted money on it, so let's do this without the cloud machine.

##### **Qazalin** [[00:26:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1576)]
I fixed some Python-time issues and merged bug fixes. Startup time is about half what it was.

##### **Geohot** [[00:26:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1585)]
What is startup time now?

##### **Qazalin** [[00:26:29](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1589)]
About three minutes. The first step takes 97 seconds, and the rest is the serialized data loader. We can parallelize that.

##### **Chenyu** [[00:26:54](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1614)]
It's three minutes now?

##### **Qazalin** [[00:27:02](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1622)]
It was six minutes.

##### **Geohot** [[00:27:05](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1625)]
So we're still wasting three minutes.

##### **Qazalin** [[00:27:13](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1633)]
The 97 seconds is scheduling.

##### **Geohot** [[00:27:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1636)]
One second per step will beat them.

##### **Qazalin** [[00:27:20](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1640)]
I can look at the data loader.

##### **Geohot** [[00:27:24](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1644)]
Don't worry about that now; focus on the stalls. Does this run start around 1.12 seconds?

##### **Qazalin** [[00:27:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1657)]
It starts around 1.12 and stabilizes around 1.2.

##### **Geohot** [[00:27:47](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1667)]
We can't rely on the starting speed.

##### **Qazalin** [[00:27:50](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1670)]
It stabilizes around 1.22.

##### **Geohot** [[00:27:55](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1675)]
We need 1.06.

##### **Qazalin** [[00:28:07](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1687)]
Once the run is stable, I'll get a better breakdown.

##### **Geohot** [[00:28:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1696)]
Hit 1.06, warm the computers, and improve from there. We could use the cloud for the final run, but I want to beat AMD here.

##### **Qazalin** [[00:28:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1717)]
These computers are hot.

##### **Geohot** [[00:28:39](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1719)]
Run it at night.

##### **Qazalin** [[00:28:44](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1724)]
The cloud machine still needs driver support.

##### **Geohot** [[00:28:54](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1734)]
Take the cloud machine off the table. We spent $120 and got nothing.

##### **Qazalin** [[00:29:04](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1744)]
Yeah, it timed out. I'm not sure how to debug it.

##### **Geohot** [[00:29:08](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1748)]
That's outside our control. Our own machines are within our control, and this is probably just the air conditioning. Hit 1.06.

##### **Qazalin** [[00:29:27](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1767)]
Okay. I'll work with the hot machines.

##### **Chenyu** [[00:29:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1776)]
Anything else?

##### **Qazalin** [[00:29:40](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1780)]
That's all.

##### **Chenyu** [[00:29:40](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1780)]
Okay, moving on.

##### **Geohot** [[00:29:46](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1786)]
I've made some progress. I got rid of `BIND`, so variables are now treated like any other buffer; they just have a different address space. That really simplifies the new rangeify because it doesn't need special cases for variables. It's passing most tests, though the new code still has failures.

##### **Geohot** [[00:30:17](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1817)]
I also want to change the behavior of `CONTIGUOUS`. Currently, `CONTIGUOUS` is transformed and given a buffer in rangeify. I don't think it should be. It can remain `CONTIGUOUS` in rangeify, meaning that buffer won't make its way back to the tensor graph. If you want a buffer in the tensor graph, you have to use `CLONE`.

##### **Geohot** [[00:30:40](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1840)]
`CLONE` creates a numbered, unique buffer. `CONTIGUOUS` won't do that; it will still be a kernel, but it will be a kernel break. `CONTIGUOUS` and `STAGE` are then the same thing. My next deletion is to make a high-level `CONTIGUOUS` insert a lower-level `STAGE` that says to stage this in global memory.

##### **Geohot** [[00:31:06](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1866)]
There's been a lot of simplification. `STAGE` is here to stay. It means to create a buffer and store while ending these ranges. You can also partially stage things, which should let us express pretty much everything.

##### **Chenyu** [[00:31:32](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1892)]
What exactly is `STAGE`?

##### **Geohot** [[00:31:33](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1893)]
It's buffer creation and ending a range in one thing. We might also have a variant of `STAGE`, or something else, that does `MULTI`. Right now we handle `MULTI` by pushing it through movement ops. With the new rangeify, we should move away from that and make it more like a restriction: when this range reaches the `MULTI` op, it needs to be on a particular device or warp. It will rewrite ranges lower in the graph, and in some cases say the operation is invalid.

##### **Geohot** [[00:32:35](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1955)]
The new rangeify is coming along. That's the first step: a clean-slate rangeify. Oh, GitHub is back.

##### **Geohot** [[00:32:51](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=1971)]
Hopefully the new rangeify makes sense. You can see the TODO in there for a merging and splitting algorithm. We currently do merging and splitting in a lot of ad hoc places. Instead, we probably want an initial pass like the one in this PR: "add safe STAGEs to never duplicate compute."

##### **Geohot** [[00:33:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2005)]
That adds `STAGE`s so compute is never duplicated. Merging and splitting can happen later to decide whether we want to duplicate some compute. Some stages will resolve to not duplicating compute and can be removed entirely. Take a ReLU with children: one path goes to a `COMPARE` and another to a `WHERE`. During rangeify, you can't know whether those children will resolve to the same ranges, so you insert a `STAGE` and remove it later if it isn't needed.

##### **Geohot** [[00:34:08](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2048)]
We also refactored custom kernels so they don't have a user `CONTIGUOUS`. The real solution is to add a rule at the very end saying that you need to split before custom kernels. That's a correctness rule because you need a real buffer there. We can add it as a rule instead of vaguely maintaining that property throughout the pipeline.

##### **Geohot** [[00:34:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2085)]
Rangeify 2 deletes both the old rangeify and indexing. There's no more indexing. You take a `STORE` with a shape, put two `INDEX`es on it, and migrate those indexes up the graph, consuming all the movement ops along the way. I'll add `STAGE` to the spec because that one is here to stay.

##### **Geohot** [[00:35:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2119)]
The other thing I've been working on is the custom MEC. The repository is private now, but everyone here should be able to see it.

##### **Chrism** [[00:35:39](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2139)]
Oh, it works.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2140)]
It's a fully working custom MEC. What I really like is that it shows all the real things the GPU is doing. It clarifies what happens when a GPU dispatches work and helps set things up for writing our own operating system. We don't need to rewrite the MEC for our OS; we'll dispatch about 96 long-running kernels, and those kernels will handle everything.

##### **Qazalin** [[00:36:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2185)]
Interesting.

##### **Geohot** [[00:36:29](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2189)]
We want to replace all this GPU dispatch machinery with local dispatch machinery that runs on the cores. Once we have that, it's clear what future hardware should look like: independent cores with their own communication primitives. You already have to deal with that one layer up from a multi-GPU perspective. There's no dispatch across multiple GPUs and no MEC that spans them. There isn't even one MEC spanning an entire MI300; it has eight MECs.

##### **Chenyu** [[00:37:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2242)]
Is this Kimi?

##### **Geohot** [[00:37:24](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2244)]
Yeah, this is Kimi.

##### **Chenyu** [[00:37:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2246)]
It's pretty good.

##### **Geohot** [[00:37:28](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2248)]
It's pretty good, though it required a lot more prompting than I would have liked. I probably spent 100 million tokens on this. This is also a distillation of the first attempt. It built an entire custom MEC in tinygrad with far too much complexity, so I told it to keep only the minimum needed.

##### **Chenyu** [[00:38:03](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2283)]
Cool. Anything else?

##### **Geohot** [[00:38:06](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2286)]
I've got to add `STAGE` back to the spec. `STAGE` is real.

##### **Chenyu** [[00:38:11](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2291)]
Good. Okay, next is my stuff.

##### **Chenyu** [[00:38:21](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2301)]
I want all `CONST`s to have weak dtypes. I've made good progress: right before dtype decomposition, every `CONST` now has a weak dtype and only a weak dtype. I removed all strong-dtype `CONST`s before decomposition and made sure everything still runs correctly. It took a while because other code depended on strong dtypes, but those paths are now cleaner. I have a fairly large PR that works for Metal, Clang, and the C-style backends, and makes sure `CONST`s remain weakly typed through the rest of the flow.

##### **Chenyu** [[00:39:17](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2357)]
It still needs work before it can merge. It exposed issues in dtype decomposition and the order in which we do things, which I'll clean up. That gets through some of the backends; then I need to study how it works with assembly backends. Overall, it's making good progress.

##### **Geohot** [[00:39:44](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2384)]
Are you confident we'll be able to remove dtype from `CONST`?

##### **Chenyu** [[00:39:48](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2388)]
Yes. While doing this, I also found bugs that had been there for two years. Having a dtype on `CONST` was too convenient, so a lot of code came to rely on it.

##### **Geohot** [[00:40:08](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2408)]
It's good to get that cleaned up. Do you know why the "variables should not be weakints" PR is failing?

##### **Chenyu** [[00:40:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2419)]
Some of it is probably a bad test setup. We have variables whose ranges exceed int32, and forcing those to int32 will fail. Another thing that might matter is that a variable can lower to `AddrSpace.ALU` in a symbolic `RANGE`. I don't know whether that's the issue here.

##### **Geohot** [[00:40:54](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2454)]
Should I work on that PR, or is it related to what you're doing?

##### **Chenyu** [[00:41:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2460)]
It's not really related. See whether the failure is just a bad test. If you think it's a lowering issue, I can take a look. There's a function somewhere that checks whether a range fits in int32. It uses int32 if it does and int64 otherwise.

##### **Geohot** [[00:41:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2496)]
I shouldn't hardcode it. I'll use the function that checks the range. The basic logic is that variables are buffers, and buffers should never have weak dtypes. Do you agree?

##### **Chenyu** [[00:41:57](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2517)]
Yeah. It's a little tricky because when you put a `CONST` into it, that `CONST` has a weak dtype. It's like putting something into a container with a different dtype, but that's probably fine.

##### **Geohot** [[00:42:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2536)]
That should be fine. Dtype broadcasting should let you store a weak int into an int buffer.

##### **Chenyu** [[00:42:24](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2544)]
Check what's happening in the test. If something inside tinygrad is wrong, I can take a look.

##### **Geohot** [[00:42:35](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2555)]
I'll check the minimum and maximum values and promote it if it doesn't fit in an int.

##### **Chenyu** [[00:42:40](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2560)]
There are annoying questions like whether to use int or uint and whether it can be negative, but int should be fine.

##### **Geohot** [[00:42:50](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2570)]
I think int is right.

##### **Chenyu** [[00:42:54](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2574)]
I'll see where I am at the end of this week. It should be done during this two-week sprint.

##### **Chenyu** [[00:43:07](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2587)]
Another small thing I've worked on intermittently is the Python Torch backend, because it's fun. I found some bugs and fixed several small things. Now I'm having agents pull random Torch code and see whether it works. We'll also get `torch.compile` soon, which will be nice.

##### **Geohot** [[00:43:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2616)]
Is there a clean way to do that? Are you working on it?

##### **Chenyu** [[00:43:39](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2619)]
Yes. `torch.compile` exposes a lower-level form, and we can hook the JIT into it.

##### **Geohot** [[00:43:51](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2631)]
Great. It would be good to have Torch as a real frontend.

##### **Chenyu** [[00:43:55](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2635)]
Some of the slowdown comes from symbolic rewrite rules, including `INDEX`-related rules and UOp value analysis. Some are very slow and consume a lot of BEAM time. I'll try to mitigate that. I want the benchmark to be much faster, not 30 minutes per job.

##### **Geohot** [[00:44:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2666)]
We want all tests under three minutes.

##### **Chenyu** [[00:44:31](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2671)]
The benchmark can be slightly longer, but definitely not 30 minutes per job.

##### **Geohot** [[00:44:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2676)]
Three minutes. It shouldn't be slow. If we BEAM all the kernels at once, or just compile all the kernels at once, it should be much faster.

##### **Chenyu** [[00:45:12](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2712)]
I think the Python and rewrites are slow now.

##### **Geohot** [[00:45:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2719)]
Improving that is totally orthogonal to improving the packing.

##### **Chenyu** [[00:45:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2726)]
I think half of the BEAM time is now spent in rewrite rules. Okay, let's move on to `SLICE`.

##### **Chrism** [[00:45:36](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2736)]
`SLICE` is gone. I didn't end up implementing variable offsets. I should see whether that's easier now that variables are similar to buffers, because that was making it tricky. Variable offsets would make it much easier to remove sub-buffers: the buffer class could have an `_offset`, and CL and WebGPU would expose the same API.

##### **Chrism** [[00:46:24](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2784)]
Most of this work happens in `pm_copy_from_store`, or whatever it's called.

##### **Geohot** [[00:46:41](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2801)]
If we want variable offsets, we have to improve the SDMA compiler.

##### **Chrism** [[00:46:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2805)]
Yeah. It's related to the cross-device work too. That may be worth doing, especially if it would help the LLaMA speed.

##### **Geohot** [[00:47:02](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2822)]
Is our Gitea CI passing?

##### **Chrism** [[00:47:05](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2825)]
It's better than it was. That's more of what I've been working on.

##### **Geohot** [[00:47:10](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2830)]
That link is public. HCQ2 is failing.

##### **Chrism** [[00:47:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2834)]
It looks like it's running out of memory, which is interesting because namespace doesn't get remotely close to six gigabytes. I'm not sure why it's failing, so I'll investigate it.

##### **Chrism** [[00:47:26](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2846)]
The QCOM compile-only test is no longer a platform test. It can now run on x86 and on my Mac. I did that with a small compile server that runs in either QEMU or Docker. We should generalize it for NVRTC and NVJitLink so that, when someone plugs a Chestnut into a Mac and wants to use an NVIDIA GPU, it doesn't spin up Docker for every compilation.

##### **Chrism** [[00:48:12](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2892)]
I wanted to put everything on Gitea, but hosting the Docker image there could point a lot of traffic at the Gitea instance.

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2902)]
What would the Docker image contain?

##### **Chrism** [[00:48:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2905)]
NVJitLink and NVRTC.

##### **Geohot** [[00:48:30](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2910)]
We should put Cloudflare in front of it so people aren't repeatedly downloading the same data.

##### **Chrism** [[00:48:41](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2921)]
I mean everyone who installs tinygrad.

##### **Geohot** [[00:48:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2925)]
Right, which is why we should put a Cloudflare proxy in front of it. The site is already going through Cloudflare, but only through a forwarder, not an intelligent proxy. We want the release URLs to hit the proxy. I'll give you access to the Cloudflare account if you don't have it. We also need to build these dependencies into Docker.

##### **Chrism** [[00:49:28](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2968)]
That was going to be the trial run for getting everything into Docker. We'd publish both the sysroots and Docker images, so people could download either a tarball or an OCI image.

##### **Geohot** [[00:49:53](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=2993)]
I would use `nektos/act` in the Docker image to pre-download all the dependencies.

##### **Chrism** [[00:50:06](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3006)]
Why not build a Docker image containing all the shared objects and anything else we need?

##### **Geohot** [[00:50:10](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3010)]
That sounds nice, but we want this to keep working on GitHub too. `act` can read the YAML and build the Docker image. Just have one generic setup environment in a roughly 20-line YAML file.

##### **Chrism** [[00:50:35](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3035)]
I understand, but it will produce a larger image.

##### **Geohot** [[00:50:42](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3042)]
It should never leave the machine. We can have a job here that builds Docker whenever it changes. Why do we care if the local image is 40 gigabytes?

##### **Chrism** [[00:51:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3060)]
Okay, sure. That's fine.

##### **Geohot** [[00:51:04](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3064)]
It's a little offensive, but the default Ubuntu runner image is already around 24 gigabytes. I also set up our first T-series machine, TinyT1. T is for Turin. It has a 128-core CPU, though that doesn't give as much parallelism as you might expect because the work is often memory-bound.

##### **Chenyu** [[00:51:42](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3102)]
The current slowdown is actually because we're network-bound. Cache the whole environment.

##### **Chrism** [[00:51:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3112)]
We'll fix that. I'll also investigate what the HCQ2 test is doing. Better error messages would be useful, but the process is getting OOM-killed, so I'm not sure whether we can get one. Maybe we can disable the OOM killer by disabling overcommit. Then `malloc` will return a failure and show an error message.

##### **Geohot** [[00:52:29](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3149)]
That's a good idea. Disabling overcommit is a good idea anyway.

##### **Chrism** [[00:52:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3157)]
That's probably what I'll work on this week: getting this into good shape. The only annoying part is that disabling overcommit also disables swap, or at least requires being intelligent about it.

##### **Geohot** [[00:52:54](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3174)]
I don't want swap. It'll swap to an SSD and wreck the SSD. If necessary, we can put more RAM in the computer. RAM is just expensive. We can debate whether our computers should have 192 or 384 gigabytes.

##### **Chrism** [[00:53:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3194)]
We'll try six gigabytes per runner for a while and see whether it causes issues.

##### **Geohot** [[00:53:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3199)]
I actually configured eight gigabytes per runner because some runners really do use that much. It's four cores and eight gigabytes per runner, the same as namespace, so I don't understand why this is breaking.

##### **Chrism** [[00:53:29](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3209)]
Something odd is happening with that HCQ2 test. Moving on to comma's big model: they're running it, and we have our benchmarks. I keep telling them that the API boundary requires `compile3.py` to closely match what they run. They can't put hacks in their model compilation script and expect us to know what they changed and reproduce it.

##### **Chrism** [[00:54:05](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3245)]
Hopefully that gives them an incentive to make needed changes in tinygrad so we benchmark the thing they actually care about.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3261)]
After HCQ2, I want to refactor the entire JIT so that the saved artifact is a single UOp. They would need a script that produces a UOp, and then we've separated running from compilation.

##### **Chrism** [[00:54:38](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3278)]
They've also mentioned moving away from exporting ONNX and instead implementing a small runner in tinygrad.

##### **Geohot** [[00:54:49](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3289)]
That does nothing by itself.

##### **Chrism** [[00:54:49](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3289)]
It gives them Flash Attention.

##### **Geohot** [[00:54:53](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3293)]
Oh, they want to start writing custom kernels. That's more API to maintain. I've been trying for days to get the generic delta-attention scan merged. We need a scan.

##### **Chrism** [[00:55:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3316)]
If they keep saying they want Flash Attention, that's how they'll get it for now.

##### **Chenyu** [[00:55:21](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3321)]
They can't really be blocked only by Flash Attention, right?

##### **Chrism** [[00:55:27](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3327)]
My impression is that they aren't, but I don't know.

##### **Geohot** [[00:55:33](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3333)]
The new rangeify will give us scan for free too. It will be an explicit scan where you allocate a buffer and store to it. You can write the reduction explicitly in buffer-store form in the big graph.

##### **Chenyu** [[00:55:58](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3358)]
Anything else?

##### **Chrism** [[00:56:00](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3360)]
No, I think that's it.

##### **Chenyu** [[00:56:04](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3364)]
I don't see RDNA3. Oh, there's PR 17519: "fix call arg indexing in shard scheduling."

##### **Geohot** [[00:56:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3385)]
17519. Zero-offset `SHRINK`...

##### **Chrism** [[00:56:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3412)]
Maybe it's possible not to create this at all.

##### **Geohot** [[00:56:58](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3418)]
I'm just going to merge this. It's fine. Okay, I merged it.

##### **Chenyu** [[00:57:12](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3432)]
Does anyone want to comment on RDNA3? Thomas is back.

##### **Raine** [[00:57:17](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3437)]
Do you want me to talk about RDNA3?

##### **Chenyu** [[00:57:20](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3440)]
Sure.

##### **Raine** [[00:57:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3442)]
I haven't had much time this week because I've been traveling, but I fixed compile times, got MNIST and LLaMA running, and fixed several more tests. Now I'm down to just the FP16 GEMM. It wasn't compiling because LLVM explicitly schedules WMMAs in blocks. Our linearizer places all the loads at the top, which forces all the register values to remain live for the entire kernel. I wrote an explicit scheduler that isn't fully working yet, but it reduces register pressure enough for the kernel to compile. This week I'll try to get that last test and ResNet training passing, then speed up MNIST and LLaMA.

##### **Geohot** [[00:58:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3494)]
I see several other failures on the PR.

##### **Raine** [[00:58:18](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3498)]
Those are from the last commit or two because I've been experimenting. I probably shouldn't have pushed that yet. It was part of trying to fix the FP16 GEMM because it has so many WMMAs. I'm realizing that LLVM does scheduling optimizations under the hood that you don't notice. We may need more infrastructure as we introduce custom backends so register pressure doesn't get too high.

##### **Geohot** [[00:58:49](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3529)]
Ideally, register allocation and linearization happen together.

##### **Raine** [[00:58:58](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3538)]
LLVM has an approximately 1,800-line file that does this explicitly for WMMA kernels, with many ways to solve it optimally. My solution reduces the pressure of a 64-by-64 GEMM by around 40 VGPRs in about 50 lines.

##### **Geohot** [[00:59:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3562)]
I don't want any of that. Delete it. I never want something that looks like a WMMA scheduling policy; that's not the solution. The solution should use an ILP solver to jointly determine memory and register allocation. We're never going to merge something like a WMMA interleave pressure reducer.

##### **Raine** [[01:00:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3619)]
Okay.

##### **Geohot** [[01:00:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3622)]
If it's really just one test, I'd rather skip that test for the RDNA3 backend and get the backend merged.

##### **Raine** [[01:00:28](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3628)]
That's what I was wondering. Before that PR, only the FP16 GEMM test fails. I thought it might be important because LLVM doesn't have a general solution either; it has WMMA-specific policies. But a more general solution is fine.

##### **Geohot** [[01:00:48](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3648)]
Skip that test for now and focus on getting this merged. The right solution is joint: you can't independently do register allocation and linearization. It's the same problem as memory layout. Executing kernels in a different order can reduce maximum memory pressure, and we want something that can solve that generally.

##### **Raine** [[01:01:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3679)]
Okay. Is the MNIST speed good enough? I'm also going to run LLaMA with BEAM. I was getting repeated errors when I tried BEAM, though it seems to work today.

##### **Chrism** [[01:01:42](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3702)]
Are you setting `IGNORE_BEAM_CACHE`, or deleting the BEAM cache? You may have bad data in it.

##### **Raine** [[01:01:46](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3706)]
No. It wasn't just failing to run BEAM; it was spamming errors.

##### **Geohot** [[01:01:56](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3716)]
I would still skip the cache. It can be in any state.

##### **Raine** [[01:02:07](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3727)]
Should I focus on getting ResNet to compile and checking the speeds? I also need to fix `TUPLE_ORDER`.

##### **Geohot** [[01:02:19](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3739)]
Everything should work, and the total MNIST time should be within 2x of LLVM. Is it?

##### **Raine** [[01:02:30](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3750)]
Yeah, with `CACHELEVEL=0`.

##### **Geohot** [[01:02:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3757)]
Right, `CACHELEVEL=0`. I don't care about BEAM for this measurement. Just run MNIST without BEAM and with `CACHELEVEL=0`. Let me check your branch now.

##### **Raine** [[01:02:57](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3777)]
It's slightly broken. You might have to go back one commit.

##### **Geohot** [[01:03:01](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3781)]
It's not easy for me to go back. I'll try it next time.

##### **Raine** [[01:03:12](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3792)]
I'll run it and post the assembly.

##### **Geohot** [[01:03:16](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3796)]
If I run `beautiful_mnist.py` right now with `DEV=AMD:RDNA3`... You have some `TUPLE_ORDER` issues. Run with `TUPLE_ORDER=0`.

##### **Geohot** [[01:03:49](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3829)]
I think your cache is doing a lot of work. This hasn't run anything yet. Okay, there it goes; it ran the first step. The kernel times look fine.

##### **Raine** [[01:04:04](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3844)]
MNIST was pretty quick compared with LLaMA.

##### **Chenyu** [[01:04:08](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3848)]
Is this actually working?

##### **Geohot** [[01:04:15](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3855)]
There's an initial part that's pretty slow, but that might just be TinyRed. These times look great. As long as both Python time and model time are within 2x end to end, it's fine.

##### **Raine** [[01:04:37](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3877)]
If I remove the scheduling code, some FP16 GEMMs will be extremely slow. I'll have to add spilling for them to compile at all, and there will be a lot of loading.

##### **Geohot** [[01:04:53](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3893)]
That's okay. It's never worth trading complexity for speed on a specific case. Those approaches never scale and always end up being deleted. This is working well; the programs and disassembly look beautiful.

##### **Raine** [[01:05:33](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3933)]
I've been looking at LLVM and trying to get as close as possible.

##### **Geohot** [[01:05:38](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3938)]
LLVM looks ugly. This looks much better. I was looking at a normal CONV kernel, and this is much more beautiful than what LLVM produces. LLVM spams things everywhere.

##### **Raine** [[01:05:59](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3959)]
It does a lot of optimization with SGPRs.

##### **Geohot** [[01:06:04](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3964)]
I don't think it's faster.

##### **Raine** [[01:06:06](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3966)]
Not on most kernels.

##### **Geohot** [[01:06:08](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=3968)]
Most of those LLVM optimizations are probably cruft built on top of cruft. This isn't a big deal, and don't change it before the merge, but there's an ordering issue here. It will be slow because you have `v40` dependencies from one instruction to the next. Eventually we'll put an optimizer in there. For now, make this as simple as possible and get it merged.

##### **Raine** [[01:06:51](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4011)]
For the merge, do you want other models to be fast? What are the criteria?

##### **Geohot** [[01:06:58](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4018)]
I don't want any insane bottlenecks except for the FP16 GEMM we discussed.

##### **Raine** [[01:07:11](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4031)]
Okay, I'll clean it up this week.

##### **Geohot** [[01:07:13](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4033)]
The FP16 GEMM must still be correct; it's okay if it's slow. Spilling is okay. We also shipped your hardware: a Chestnut and a 7900.

##### **Raine** [[01:07:35](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4055)]
I'm very happy about that. Thank you.

##### **Chenyu** [[01:07:41](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4061)]
Cool. Anything else for the meeting?

##### **Raine** [[01:07:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4072)]
One more thing: can we merge the coalesce PR?

##### **Chenyu** [[01:08:03](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4083)]
Is there something wrong with it?

##### **Raine** [[01:08:05](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4085)]
It doesn't affect the other backends. These are valid buffer sizes, and if coalesce packages them into a `SHRINK`, I can lower them more easily.

##### **Geohot** [[01:08:14](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4094)]
I'm less worried about adding length 6 than I am about setting `must_divide=False`. Are you sure that's okay? Did you test this on real hardware or run tests outside your backend?

##### **Raine** [[01:08:25](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4105)]
I'll double-check. I haven't run other-backend tests with this exact change. I may have exercised it while comparing with LLVM, but I'll run a test.

##### **Geohot** [[01:08:43](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4123)]
If I merge this, what are the odds it breaks `update_benchmark`?

##### **Raine** [[01:08:49](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4129)]
I don't know. I can run a test and post the assembly.

##### **Geohot** [[01:08:54](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4134)]
Understand what `update_benchmark` does before asking me to merge a change like this, and determine whether you think it will break. We don't test this on the real hardware. Are those unaligned accesses okay? This relaxes several conditions and could break real hardware.

##### **Chenyu** [[01:09:22](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4162)]
George, can you review the two PRs?

##### **Geohot** [[01:09:27](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4167)]
Yes. I'll review them today. I'll at least review expert gating; GPT-OSS is a lot more work.

##### **Wozeparrot** [[01:09:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4185)]
One more: do we want to tag a release this week?

##### **Chenyu** [[01:09:52](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4192)]
No. Let's release after CI has been stable so we're sure everything is good.

##### **Wozeparrot** [[01:10:05](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4205)]
The original plan was to do a release with the Chestnut launch, but that didn't happen.

##### **Chenyu** [[01:10:10](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4210)]
It's too late now, and I don't think the repository is in a good state. Let's prioritize making CI and the benchmarks reliable so we're sure everything is good. Unless we learn that a new release would help a Chestnut customer, we can wait.

##### **Chenyu** [[01:10:45](https://www.youtube.com/watch?v=YtVlJ4tgJco&t=4245)]
Sounds good. That's it for this meeting. Thank you, everyone. See you next week. Bye.
