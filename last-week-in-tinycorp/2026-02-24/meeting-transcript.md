# 2026-02-24 Meeting

### Meeting Agenda

**Time:** new meeting #8
- company update
- open issue from comma
- assign, multi, disk, bitcast
- drivers
- compiler renderer, image
- llama training loop
- CALL/PARAMS

### Audio

[Youtube Link](https://www.youtube.com/watch?v=W_ZqetFXrK4)

### Highlights

- **[Company Update](#geohot-000000)**: Team is moving into the Hong Kong office with minimal setup so far (desks/chairs, tiny box), internet arriving the same day, and proper power/plugs expected Thursday.
- **[Blackwell Price Increase](#geohot-000051)**: NVIDIA raised Blackwell pricing (reported as +$1,500 each), pushing the quoted system price up and hurting margins.
- **[Comma USBGPU Regression](#geohot-000225)**: A high USBGPU overhead regression is blocking comma; the team wants to measure it clearly, then either fix or revert the offending change.
- **[Command Buffer Patching Optimization Idea](#geohot-000552)**: Geohot proposes replacing slow Python HCQ JIT patching with tensor-based buffer updates (using setitem-assign) to speed command buffer construction.
- **[CI Plan for Comma Devices + USB GPUs](#geohot-000850)**: Team discusses adding USB GPUs (e.g., 9060s) to comma CI devices / comma 4s to reproduce and monitor issues in CI.
- **[Multi / Disk / Bitcast Cleanup Direction](#chenyu-001131)**: Chenyu reports progress on multi looking more “view-like,” disk/tinyfs fixes, and identifies shape-changing bitcasts on disk as a scheduler pain point to remove.
- **[No Shape-Changing Bitcasts on Disk](#geohot-001258)**: Geohot pushes to eliminate shape-changing bitcasts and instead make disk follow the normal compiler path with rewrite rules, reducing special cases.
- **[AMD/CDNA Stability Debugging Priority](#geohot-001951)**: The team prioritizes reproducing and understanding AMD/CDNA bad states (HTQ timeout / discovery signature mismatch), treating 30s timeouts as serious failures and gathering evidence to escalate to AMD.
- **[Renderer API Needs Better User Stories](#geohot-002923)**: In reviewing the new renderer API proposal, Geohot argues the design still needs more thought (device/render/arch targeting, heterogeneous export) and asks for more user-story-driven refinement.
- **[Image Path Performance Gap](#chrism-003119)**: Chrism narrows an image-mode slowdown to extra kernels plus one slower kernel; Geohot prioritizes matching kernel count first before spending time on Qualcomm compiler quirks.
- **[Cast/Materialization Scheduling Rule Direction](#geohot-003343)**: Geohot suggests fixing graph split behavior around `cast half -> cast float` chains (instead of using `contiguous`) so casts associate correctly and avoid unnecessary kernels.
- **[Llama Training Loop Bottleneck + Fuse Optim Path](#wozeparrot-004119)**: Wozeparrot reports completed/ongoing Llama runs (optimizer offloading vs model parallel), while the team identifies fused optimizer work and gradient layout changes as the main path to speedups.
- **[Large Contiguous Gradient Buffer Plan](#geohot-004328)**: Geohot proposes assigning each gradient into slices of one large zeroed gradient tensor so fuse-optim can operate on one contiguous buffer instead of many small gradient buffers.
- **[Linear Schedule Refactor and Nested Calls](#geohot-005124)**: Geohot describes a major refactor toward a single linearized schedule graph with nested calls, removing “outer/inner world” special casing and making JIT behavior much cleaner.
- **[Remote GPU over Network Vision](#geohot-005543)**: Long-term direction: expose GPUs on remote machines through a server abstraction (memory-space oriented), enabling normal workflows to target remote RDNA4/USB GPUs and eventually scale across many machines.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=0)]
Okay, welcome everyone. Start the meeting with company update.

##### **Geohot** [[00:00:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=11)]
Yeah, everything's kind of getting moved into the Hong Kong office. We got a couple of mishmash desks and chairs. We got a tiny box. We're getting internet today. We're getting plugs on Thursday.

##### **Chenyu** [[00:00:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=24)]
What on Thursday?

##### **Geohot** [[00:00:26](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=26)]
Plugs. Electricity.

##### **Chenyu** [[00:00:28](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=28)]
Oh, great.

##### **Geohot** [[00:00:30](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=30)]
Right now we have one plug and it's kind of mediocre.

##### **Geohot** [[00:00:35](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=35)]
Great. Yeah, that's kind of the main thing. Any mocks getting more expensive?

##### **Geohot** [[00:00:51](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=51)]
Oh, yeah. NVIDIA raised the prices of the Blackwells.

##### **Geohot** [[00:00:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=58)]
We literally... It went to 65K, but that literally... That doesn't even... We lose margin now. That doesn't even maintain our margin.

##### **Wozeparrot** [[00:01:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=66)]
I see.

##### **Geohot** [[00:01:08](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=68)]
60 was a little aggressive last time, but yeah, no, now NVIDIA raised the price of the Blackwells

##### **Geohot** [[00:01:12](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=72)]
$1,500 each. Oh. I mean, it was surprising how cheap they were, considering they have so much RAM on them. Yeah. That's a good thing. Yeah, no.

##### **Chenyu** [[00:01:49](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=109)]
Let's just say that those companies have seen all of us on the spectrum. Yeah.

##### **Nimlgen** [[00:01:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=114)]
They love yourself.

##### **Geohot** [[00:01:55](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=115)]
Yeah, that like when. I look at Diddy, I find it just kind of... People put me up because I just feel so lost. a friend of yours about this and just kill yourself. open code against it and I wanted to run some model reasonably.

##### **Geohot** [[00:02:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=125)]
Okay, sounds good.

##### **Chenyu** [[00:02:10](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=130)]
Next item is a new thing, but let's go through open issues for Karma. I see Woz Perry will say something.

##### **Geohot** [[00:02:25](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=145)]
Karma is complaining because USBGP overhead is very high.

##### **Wozeparrot** [[00:02:30](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=150)]
So C-type structure actually increased overhead too.

##### **Geohot** [[00:02:37](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=157)]
Yeah, I haven't had a chance to look into that yet.

##### **Wozeparrot** [[00:02:42](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=162)]
If you look at the issue, there's a patch in the issue. I don't know if it's... It looks kind of weird, but...

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=172)]
It's definitely not a good patch. Yeah. Yeah, I mean, we need to fix that or if it's just slower, we need to revert it.

##### **Chrism** [[00:02:59](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=179)]
Yeah.

##### **Chenyu** [[00:03:01](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=181)]
So let's start by logging this somewhere.

##### **Geohot** [[00:03:08](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=188)]
Yeah, we have to figure out a good task for this. Yeah.

##### **Chenyu** [[00:03:12](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=192)]
Yeah, I mean, if it's something that is similar to our current assert, just find a place, log it, then assert on that.

##### **Nimlgen** [[00:03:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=200)]
Yeah.

##### **Chrism** [[00:03:21](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=201)]
Yeah. Yeah. I don't currently have a USBGP on my desk, but I can get one.

##### **Geohot** [[00:03:29](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=209)]
I mean, yeah, you're in the home of USBGP and stuff.

##### **Chrism** [[00:03:32](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=212)]
That's true.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=213)]
Grab the one off my desk.

##### **Geohot** [[00:03:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=216)]
No, Henry took it, but I will get another one.

##### **Chenyu** [[00:03:41](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=221)]
Okay. Anything else that Karma is currently complaining?

##### **Geohot** [[00:03:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=226)]
That's the only complaint.

##### **Wozeparrot** [[00:03:47](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=227)]
They said that if that is fixed, they're able to use USBGP. We also have to, Cisco has made kind of that leakyvoid type thing.

##### **Wozeparrot** [[00:03:53](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=233)]
So the comments on Halloween people who use it is anabolic, disagreement between you and

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=240)]
you, squ последット fanno, but I'm thinking we're gonna deal with that bit later on as Right. And so. And it looks like they're question about whether or not in my main situation, I can timelines too low and I should at least That's not a false commentary rule, is it? Hopefully we should. Okay.

##### **Nimlgen** [[00:04:17](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=257)]
Okay.

##### **Chenyu** [[00:04:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=258)]
It looks like kitty leak is already writing out something written on, if any, just like if Because there's a click on antioxidant. to get the number you cited, right? Like somewhere in the CI, if we can make that clear for the numbers, then you can even assert on the whole thing. It's more difficult for OpenPilot because the way they run the model, but maybe for USBGPU, it's more clear.

##### **Geohot** [[00:04:39](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=279)]
We have, I mean, how much of this is the COMET device itself having a crappy processor?

##### **Wozeparrot** [[00:04:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=286)]
DC COMET is the quality of the slow.

##### **Geohot** [[00:04:48](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=288)]
Because when Armand runs it on his workstation, it is significantly less . Yeah.

##### **Geohot** [[00:04:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=297)]
Yeah, I wonder how much we can do in the Qualcomm driver to avoid this kind of stuff.

##### **Geohot** [[00:05:02](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=302)]
I mean, yeah. Oh, yeah, no, you're right. It's not the Qualcomm driver.

##### **Geohot** [[00:05:13](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=313)]
Or I mean the other driver, the AMD driver, though. I mean, what if we move the AMD driver? Like how much of it is when it patches the JIT it's using Python when it should be using CI?

##### **Geohot** [[00:05:25](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=325)]
How well does set item assign work?

##### **Nimlgen** [[00:05:33](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=333)]
What?

##### **Geohot** [[00:05:34](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=334)]
How well does set item assign work? Can we start using set item assign to build the command buffers? Can we start to use set item assign to build command buffers? Oh.

##### **Chenyu** [[00:05:50](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=350)]
How does that work?

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=352)]
Well, so right now we build the command buffers. Like if you look at the HCQ JIT patching logic, it's slow because it's written in Python. But we could build a, we can put that HCQ buffer in a tensor, and then use set item assign on CPU to update all the buffer references.

##### **Nimlgen** [[00:06:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=375)]
Yeah, but I think it will still be slow for USB.

##### **Geohot** [[00:06:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=380)]
Because of the abstraction. Which abstraction? I mean, to write into VRAM. Oh. All this USB stuff, yeah. And we update it on the GPU? Not sure. Oh. How much of the time? And no.

##### **Nimlgen** [[00:06:48](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=408)]
Our. So our queue should be on the controller itself.

##### **Geohot** [[00:06:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=418)]
I see.

##### **Geohot** [[00:07:04](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=424)]
Is that slow for the, I guess the GPU accesses it fine. But yeah, no, I mean, this sounds like something you can work on. Like, let's think about how to make this faster.

##### **Geohot** [[00:07:16](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=436)]
Yeah, I'll take a look.

##### **Nimlgen** [[00:07:19](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=439)]
So I'm going to go to the GPU.

##### **Geohot** [[00:07:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=440)]
I mean, I know it's something regressed.

##### **Nimlgen** [[00:07:22](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=442)]
But it was like the fastest way I could get it back then.

##### **Geohot** [[00:07:30](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=450)]
Yeah, I mean, even if nothing regressed, like what I want to start to think about with all of these things is building the GPU command queue on the GPU.

##### **Geohot** [[00:07:43](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=463)]
It doesn't matter which memory it's in, right? If it's in the memory of the controller, it doesn't matter. The GPU can still access that. Yeah, yeah.

##### **Chenyu** [[00:08:04](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=484)]
We'll talk about that more in your item. I think for comma, let's find a way to measure it. And if we either fix that or revert that, I don't know. We pick something. So that's the unblock comma.

##### **Chrism** [[00:08:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=498)]
So while I'm here, should I put? Like one of those devices in CI?

##### **Geohot** [[00:08:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=504)]
So it's a little annoying. The comma devices currently are on Wi-Fi or Ethernet? Yeah, I mean, we'd have to use a hub. Oh.

##### **Geohot** [[00:08:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=516)]
That's one of the comments right now. One of the comments says it goes to GPU? Which one?

##### **Nimlgen** [[00:08:45](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=525)]
One of those.

##### **Geohot** [[00:08:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=526)]
One of those. Yeah, I think it was.

##### **Geohot** [[00:08:50](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=530)]
I see. I mean, we should probably get enough 9060s, and we should put them in the comma CI devices. Yeah, if you want to do that, if there's enough of them,

##### **Wozeparrot** [[00:09:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=540)]
you can put them on the two comma ports.

##### **Chrism** [[00:09:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=543)]
OK. OK, I'll see if there's extra that I can do that with.

##### **Geohot** [[00:09:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=554)]
They're bad. Oh, they're bad. OK, OK. No, no, no. Bye. Bye. Bye.

##### **Nimlgen** [[00:09:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=560)]
Bye.

##### **Geohot** [[00:09:22](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=562)]
Wait, sorry.

##### **Chrism** [[00:09:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=563)]
I think you got ..

##### **Geohot** [[00:09:25](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=565)]
Oh, no. I was just saying about, I heard we have comma 4s. And I'm like, there's people who need those comma 4s more than us. But they're bad, so it's fine.

##### **Geohot** [[00:09:33](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=573)]
Yeah. OK. Cool. That's good. Next. Oh, yeah. Yeah, if you want to get USB GPUs, put them on the comma 4s. We'll get that in CI. OK.

##### **Nimlgen** [[00:09:52](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=592)]
Cool.

##### **Geohot** [[00:09:53](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=593)]
Cool. Cool. Next is my item.

##### **Chenyu** [[00:09:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=598)]
Next is my item. That item doesn't fuse yet. So it's annoying to write.

##### **Geohot** [[00:10:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=606)]
We got to fix that thing that's in schedule. Yeah, that too.

##### **Geohot** [[00:10:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=615)]
So I merged something this morning kind of related to this that I'm very excited about. I'm very happy with. You can like, the schedule is now just a linear

##### **Geohot** [[00:10:27](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=627)]
of what kernel it runs.

##### **Geohot** [[00:10:31](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=631)]
I'll push something today that will make, I think I can at least remove the create schedules and the realizes from what you're doing.

##### **Chenyu** [[00:10:41](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=641)]
Sure. So you mean not running multiple ones? Or?

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=648)]
Well, it'll still be multiple. But I'm not sure. I mean, I'm not sure. But I'll basically like, I don't know. We'll get to this for my thing.

##### **Chenyu** [[00:10:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=654)]
OK. Sure. Yeah. I mean, that would help a lot. I was trying something when I start to hit. Because we have like disable GC on Unrealize. So we create like some weird out of memory thing because something is not free properly. I don't know. So let's. Yeah.

##### **Nimlgen** [[00:11:16](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=676)]
Yeah. Yeah.

##### **Chenyu** [[00:11:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=678)]
Yeah. Yeah. Yeah. So I'll just add up to the multi. I think now multi really looks a lot more like just a view. View-ish.

##### **Nimlgen** [[00:11:28](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=688)]
All right.

##### **Chenyu** [[00:11:31](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=691)]
And start to look into disk. The disk. So this is for . Can you check the setup is correct or something? I think I fixed it. But I also don't know if I really fixed it. So I added. I wiped some. I think it's good enough. Lows all pass before the regression. And it's currently failing. I think most of the issue is just we only check disk in a new allocate code, location code, not also the tinyFS, something like that.

##### **Nimlgen** [[00:12:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=727)]
Yeah.

##### **Chenyu** [[00:12:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=727)]
Because before moving all this disk logic, I also want to make sure the tinyFS is not broken. So I can fix these two together. So one. One annoying thing that we can quickly discuss is bitcast. So for now, we still have bitcast shape changing bitcast. And this is annoying because it has a weird shape. And it really is not element wise. So this caused a lot of issue in scheduler.

##### **Geohot** [[00:12:39](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=759)]
Where are there shape changing bitcasts? That just shouldn't be allowed.

##### **Chenyu** [[00:12:43](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=763)]
It's only on disk. When you write.

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=768)]
Oh.

##### **Chenyu** [[00:12:49](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=769)]
It goes. It's only disk. And disk is kind of special because it's kind of a fast path. Like you can just read the consecutive ones.

##### **Geohot** [[00:12:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=778)]
I mean, I think the idea with disk is not to allow shape changing bitcast, but instead to write a compiler. It's not a real compiler. But like have disk follow the same path as all the other things. And then just like compile certain things with a bunch of graph rewrite rules.

##### **Wozeparrot** [[00:13:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=800)]
So that was my approach.

##### **Chenyu** [[00:13:26](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=806)]
And I almost finished it. So basically, the idea is you never need to bitcast your view on the disk. You always bitcast your source. So you just get a bunch of thing that is you int 8. And you always just assign which lowers to a copy to a segment on the disk. I see. I think that's how we want to do it. And in that way, we can remove this path for the bitcast altogether. I think it's just some small syntax thing that we currently put in bitcast. I think that should work.

##### **Nimlgen** [[00:14:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=847)]
Right.

##### **Chenyu** [[00:14:08](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=848)]
Yeah. So if Wolfberry can help me figure out the tinyfs is good, then I can work on this.

##### **Wozeparrot** [[00:14:16](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=856)]
Yeah, the benchmark thing can be fixed.

##### **Chenyu** [[00:14:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=858)]
OK, OK, great. So I think that's it. Yeah, because I also saw bitcast causing other issues in element-wise and shape. So hopefully, these will get cleaned up. I think the special thing for disk and tinyfs would still be slightly special. But it's not that crazy. So it'll be fine. Oh, and speaking of multi, I also have a change that, OK. So now I think we have some regression that we are realizing const when we do the sharding on const or something like that. I don't think that's intentional. But I also fix that. Then similarly, I think now we are ready to write the A range. If you shard an A range like in a poppy way, then that A range will be compute on each device. OK. So I also have a change for that that I'm testing.

##### **Geohot** [[00:15:22](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=922)]
I mean, yeah, hopefully you're seeing these abstractions become a lot better with like, you can do multi now. You don't have to worry about trying to track tags or anything.

##### **Chenyu** [[00:15:31](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=931)]
Yeah, that's very good. I removed the force reshape. I am looking to a noop. We still use noop in a weird way, but it's less and less.

##### **Geohot** [[00:15:43](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=943)]
Yeah, no, I mean, there's that noop used for copy. But that'd be nice to remove. Yeah, yeah.

##### **Chenyu** [[00:15:47](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=947)]
So yeah. So I think these are all kind of related to each other. So I'm just finding ways to eventually get to the bottom of this.

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=958)]
Great. OK. That's my part. Next, we have drivers.

##### **Nimlgen** [[00:16:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=971)]
Yeah, so for the tiny-aimed A4, I think we, so we print more errors now. So we print something special to my 300 machines, which called like architecture check. So actually, it shows the tiny-aimed A4. So as for A4, I tried to run some old reduce, but it was fine. And actually, even the last, I haven't run the full run yet. So maybe it still has some issues. But even after CPU offloading, I mean, passes most steps. Yeah. So for the clean-aimed A4.

##### **Geohot** [[00:17:01](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1021)]
What's CT offloading? When you try to run on AMD4 now, does that give you an error? Or does it still HTQ timeout?

##### **Nimlgen** [[00:17:09](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1029)]
Yeah, it should print the error.

##### **Geohot** [[00:17:13](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1033)]
Right. Because all I was saying yesterday that there's some way, she's still hitting HTQ timeouts too.

##### **Nimlgen** [[00:17:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1040)]
Yeah, I've seen that. Actually, that's, I'll take a look into that. But basically, that's the Mac just dying. And actually, you can dequeue the queue.

##### **Geohot** [[00:17:32](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1052)]
I see. Is there any way we can detect this? Because we should really be treating, I used to talk about just lowering the 30 seconds down. But I don't think the answer is lowering the 30 seconds. I think it's just that we should treat any time we hit, that 30 seconds is a pretty serious failure.

##### **Geohot** [[00:17:53](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1073)]
Yeah, I see.

##### **Nimlgen** [[00:17:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1077)]
Yeah, I'll take a look at what I can do. I think AMD GPU is kind of the same. I know. I'll try to understand which instruction causes that. And yeah.

##### **Geohot** [[00:18:09](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1089)]
I mean, we should really just pause it.

##### **Geohot** [[00:18:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1091)]
Any time we can hit that HTQ timeout, something went wrong.

##### **Nimlgen** [[00:18:17](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1097)]
Yeah. But actually, all channels we have right now, we have no errors reported to them. And actually, it couldn't recover after that, because Mac stopped responding at all. So yeah.

##### **Geohot** [[00:18:34](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1114)]
And then can we still end up in discovery signature mismatch failures?

##### **Geohot** [[00:18:44](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1124)]
What was Parrot saying? Yes. I think, yeah. But what can we do about this?

##### **Nimlgen** [[00:18:56](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1136)]
I think once we are in this state, I doubt they can do anything about this.

##### **Geohot** [[00:19:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1143)]
How do they get in that state? Do we have a repeatable way to put them in that state? So I think on time AMD 4, yeah.

##### **Nimlgen** [[00:19:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1155)]
You can just do hyperbole. You can do five resets. That's what I'm aware of.

##### **Wozeparrot** [[00:19:22](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1162)]
I can put them pretty consistently into that state on three as well. If I have a train on run going, and then I let it run for 300 steps,

##### **Geohot** [[00:19:29](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1169)]
and then it controls C it, and then I high reset, it will go in that state immediately. Why does the state happen? Do we understand it?

##### **Nimlgen** [[00:19:48](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1188)]
No, not really.

##### **Geohot** [[00:19:51](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1191)]
I think this is a good project. I think we got to figure out how to, I think we got to understand. We got to figure out like, because there's something we're doing, even if we can't recover from the state, there's something we're doing that puts it in that state. We got to understand it.

##### **Geohot** [[00:20:04](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1204)]
We got to make that reproducible. Yeah. Okay. Yeah. Yeah.

##### **Geohot** [[00:20:13](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1213)]
We got to just improve stability overall with this stuff. Yeah. Every error should be thrown. Every bad state should be completely understood. And ideally we can, if we can get into a bad state that requires a reboot, we can complain to AMD about it.

##### **Nimlgen** [[00:20:35](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1235)]
Okay.

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1237)]
Can this happen with the RDNA 3 and 4 cards too, or it's just CDNA? Discovery signature thing.

##### **Nimlgen** [[00:20:44](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1244)]
Yeah, it's just CDNA.

##### **Geohot** [[00:20:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1246)]
Just CDNA. Yeah.

##### **Nimlgen** [[00:20:47](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1247)]
Yeah. It's, I think it's even like MI350 machines.

##### **Geohot** [[00:20:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1254)]
300?

##### **Nimlgen** [[00:20:56](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1256)]
Not 300. It's 350. No, no, no.

##### **Geohot** [[00:20:59](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1259)]
I know. Have you ever seen it on 300s? Okay.

##### **Geohot** [[00:21:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1263)]
Yeah. No, no. I mean, I just.

##### **Nimlgen** [[00:21:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1267)]
Yeah.

##### **Geohot** [[00:21:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1271)]
I mean, any, anything we can build to put it in that state, even if it requires our driver, we can complain to AMD about.

##### **Geohot** [[00:21:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1278)]
I mean, they need to add a real reset to this card. I think they don't want to. They have no way to add to another. Take over.

##### **Nimlgen** [[00:21:34](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1294)]
Okay.

##### **Geohot** [[00:21:41](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1301)]
We'll just make it. Okay. We'll just make it. Okay. We'll just make it. If we can, we can.

##### **Nimlgen** [[00:21:49](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1309)]
Okay.

##### **Geohot** [[00:21:50](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1310)]
Awesome. Okay. All right. Do you have a question? No. Okay, let's go to our next question. So it's a really interesting question.

##### **Nimlgen** [[00:22:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1334)]
It's a really interesting question. There's two things to talk about.

##### **Geohot** [[00:22:19](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1339)]
Okay. Let's move on.

##### **Chenyu** [[00:22:33](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1353)]
Next is Chris.

##### **Chrism** [[00:22:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1356)]
Yeah. So I wrote up an issue or a tip about what the new render API can look like. Yeah, I mean, it's kind of what I talked about last meeting, but I think I sort of fleshed out a lot of the ideas a little bit in more detail.

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1380)]
Did you see my reply?

##### **Chrism** [[00:23:01](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1381)]
Yeah, I did. I also replied to that. Yeah, I mean, obviously the names, like I'm not particularly tied to any of them. Well, think about each. Yeah.

##### **Geohot** [[00:23:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1394)]
It's not just the name. I don't understand why it's called cross arch and not just arch. Right. There's nothing for us.

##### **Chrism** [[00:23:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1400)]
Yeah, yeah. I'm not understanding.

##### **Geohot** [[00:23:22](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1402)]
Yeah.

##### **Chrism** [[00:23:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1403)]
No, no, no. That's right.

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1405)]
Yeah. Um, okay. So CC is the renderer, right? So I guess, why does it why can it not just be rendy? Why does it have to have an underscore?

##### **Chrism** [[00:23:37](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1417)]
Because so it seems like a valid use case to be able to specify both the CPU renderer and the like AMD renderer at the same time. Right. So you may say, oh, you may say, oh, I want to use. Yeah.

##### **Geohot** [[00:23:51](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1431)]
So then every device just basically has one render. I mean, we also need to canonicalize these things as strings that it can all be like put in rewrite rules.

##### **Wozeparrot** [[00:24:01](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1441)]
What if you want to use multiple renderers per device?

##### **Chrism** [[00:24:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1446)]
Yeah. So. So right now, that's not really a supported use case. In fact, you would have to. Well, you could do it as a context var. So this currently works. So you can say like, okay, like right now, I want to use this. And then later on, I want to say, okay, well, actually, you know, rewrite, you know, CPU underscore CC to be something else. And then if you call realize again, then like and get programmers again, then I believe this works. Because it accesses their renderer. And that's a property and the property recalculates.

##### **Wozeparrot** [[00:24:41](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1481)]
Why can't we have something like a target triple that's like AMD dash GFX 1100 dash?

##### **Geohot** [[00:24:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1486)]
Well, no, because it's not all a different device, right? Like the device is what memory it's. It's not like you'd want like some devices. We used to have this, but it was really bad when we had things on the CPU device and the LVM device, right? They're not different devices. Yeah.

##### **Wozeparrot** [[00:25:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1500)]
Like you can split the target trouble into how you parse it. Like the first thing. You just take the first thing. I got the target. And then that's the device. It's on.

##### **Geohot** [[00:25:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1507)]
No, but how does this work for like, we haven't talked about like, so I want to compile some stuff with playing and some stuff with all of you. How do I do?

##### **Chrism** [[00:25:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1515)]
Yeah. So, I mean, right now, the way that you would do this is you would say, you know, like with CPU, CC equals LVM, and then you do your, your, whatever you want to do. And then you would do with CPU, CC equals, you know, playing and you do whatever you want.

##### **Geohot** [[00:25:31](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1531)]
Well, I definitely like rend better than CC. I think this is fine. For now. And just have it be a context bar.

##### **Geohot** [[00:25:39](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1539)]
Yeah. And yeah, and then, um, yeah.

##### **Geohot** [[00:25:47](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1547)]
Could it be CPU underscore arch?

##### **Chrism** [[00:25:53](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1553)]
Oh, that's a good point. Well, okay.

##### **Geohot** [[00:25:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1557)]
Are you ever gonna, hmm. You have to, right?

##### **Chrism** [[00:26:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1567)]
Yeah, I guess it does.

##### **Geohot** [[00:26:09](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1569)]
I mean, it's already still, then you have the same question too, is what if I have a computer that has an RDNA 4 GPU and an RDNA 3 GPU?

##### **Chrism** [[00:26:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1578)]
Whoa, wait, wait, wait, it does not. Wait, wait, sorry, sorry. Oh yeah. Okay. That's, that's true. But then also it doesn't need to, arch does not need to be, uh, that's not, that's not necessarily true that arch needs to be, uh, per device because you, you will only ever specify arch. I mean, in theory, it's not necessarily true. In theory, you only ever specify arch for null and Python. Um, right.

##### **Geohot** [[00:26:41](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1601)]
So it doesn't necessarily need to be per device. How do I specify arch for null is what?

##### **Geohot** [[00:26:51](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1611)]
It's gonna be something like AMD colon or something.

##### **Chrism** [[00:26:55](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1615)]
So for null, what you would do is you'd say, uh, like null rend equals, you know, uh, QCOM colon CL. Okay.

##### **Geohot** [[00:27:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1625)]
And then arch equals a six 30. I see. So why is it not, why is arch just not included in the renderer then? That's that's an option.

##### **Chrism** [[00:27:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1644)]
That would work. Yeah.

##### **Geohot** [[00:27:27](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1647)]
Right. If you just put, if you just put arch in the renderer and then the renderer kind of has a triple, right? So the renderer triple is.

##### **Chrism** [[00:27:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1656)]
It's only a triple on null though, right?

##### **Geohot** [[00:27:40](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1660)]
Because, um, You can use null for compiling, right? For export. But if I want to export to forgiveness, I want to export to, so comma had this use case

##### **Wozeparrot** [[00:27:55](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1675)]
before they moved everything into one grid where the policy model was Ryan on the ball country view.

##### **Geohot** [[00:28:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1680)]
And then the vision model was on the USB. Do you think?

##### **Nimlgen** [[00:28:04](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1684)]
Okay.

##### **Geohot** [[00:28:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1686)]
So I think we've got to stop thinking about things in terms of like these discrete renderer

##### **Geohot** [[00:28:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1691)]
arch and device things. Like I think we want a triple that's those three things, right? I think it's device colon renderer, colon art or something.

##### **Geohot** [[00:28:21](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1701)]
So maybe you do want like target equals whatever. Yeah. Does targeting compass device now? Like anyway, okay.

##### **Geohot** [[00:28:34](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1714)]
Yeah. So a key thing about the arch and the, uh, and the renderer is that they don't affect the memo.

##### **Chrism** [[00:28:45](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1725)]
Yeah.

##### **Geohot** [[00:28:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1726)]
Right. But then we also have this thing where, so this requires more thoughts still, like we also have this thing where there's multiple devices, right? So how do we deal with that?

##### **Chrism** [[00:28:55](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1735)]
Yeah. How do we. Well, so I mean, this right now is parameterized over the device object, not the renderer object. Um, yeah. It feels to me like this needs to be, yeah.

##### **Geohot** [[00:29:09](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1749)]
It doesn't have anything to do with the renderer object. The renderer object should not require the opening of the device.

##### **Geohot** [[00:29:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1754)]
Yeah. Yeah, exactly. Um, yeah. So I don't know. I think this still requires more thought.

##### **Geohot** [[00:29:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1763)]
I don't exactly have all the answers, but I think that what maybe the next thing to do in is in that tip, think about different user stories and make sure you cover all of them.

##### **Chrism** [[00:29:32](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1772)]
Yeah. For sure.

##### **Geohot** [[00:29:35](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1775)]
Because, yeah, I mean, we need to be able to change render. We need to be able to, uh, like, yeah, the export to the heterogeneous system, right? Like if you're compiling on a CPU and you're doing stuff that has some stuff on the Qualcomm and some stuff on the USBGP. Yeah. That's what you meant, right?

##### **Chrism** [[00:29:52](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1792)]
Yeah. Yeah. Yeah. Yeah, exactly.

##### **Nimlgen** [[00:29:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1794)]
Yeah.

##### **Chrism** [[00:29:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1797)]
Um, so what I would say is that we're partial towards a system with fewer environment variables.

##### **Geohot** [[00:30:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1805)]
Uh, yes. And the other thing that I think is a good intermediate for this is to work on the graph rewrite such that renderer is not passed as a context variable.

##### **Geohot** [[00:30:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1820)]
Uh, context variable?

##### **Geohot** [[00:30:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1823)]
Right now, renderer is context in a lot of graph rewrites.

##### **Chrism** [[00:30:27](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1827)]
Oh, yeah. Yeah. That's that. Sorry. I got confused by context. Yeah.

##### **Geohot** [[00:30:31](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1831)]
Yeah. And it shouldn't be right. Like we want, I don't exactly know what the solution is there either, but my point is that once we produce a graph, like renderer should be taken from, right. Because it can't be a context variable because that graph rewrite can support multiple, uh, different lowerings potentially.

##### **Geohot** [[00:30:50](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1850)]
Or maybe it is just set.

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1852)]
I don't know. But yeah, these things have to be, these things have to be thought through. Like, I'm thinking about like the program you offer the program you off. Like. When we go from linear to source, the program you up needs to have not just the device on

##### **Geohot** [[00:31:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1866)]
it, but also the renderer. Yeah.

##### **Nimlgen** [[00:31:10](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1870)]
Yeah.

##### **Geohot** [[00:31:13](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1873)]
Um, well, yeah, I think, yeah, I think there's just more to do more to discuss on that tip. Uh, how's the image coming?

##### **Chrism** [[00:31:19](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1879)]
Uh, yes. So, um, I mean, I know exactly what the performance difference is right now. It's, uh, there's one kernel. Uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh, uh. Um, which is eating up, uh, uh, we're, we're, so we're about like two and a half milliseconds, a little less than two and a half milliseconds, uh, behind, uh, like image, image equals one is that it's that much slower. Um, and there's one specific kernel.

##### **Geohot** [[00:31:45](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1905)]
Um, I see three milliseconds on your, uh, cast thing.

##### **Chrism** [[00:31:50](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1910)]
Yeah. That one, that one was actually slower. I'm not going to merge that, but that I thought for whatever reason, it seemed like it was testing faster, but it wasn't.

##### **Nimlgen** [[00:31:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1917)]
Yeah.

##### **Geohot** [[00:31:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1918)]
Well, I mean, it's not, so there's still, there's 154 kernels.

##### **Chrism** [[00:32:04](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1924)]
Yeah, yeah, yeah. So that's, that's, there's, there's, those are the two problems, is that one of them is that there's more kernels. There's approximately 30 more kernels. Okay. And then there's also one kernel which appears in both cases, but it is slower in the image equals one case. And this is down to, it looks, honestly, it looks like a bug in the Qualcomm, or a failure to optimize in the, in the Qualcomm compiler, in the Qualcomm CL compiler. But I'm going to try and figure out how to get it to output the same code.

##### **Geohot** [[00:32:35](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1955)]
How much slower is it?

##### **Chrism** [[00:32:38](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1958)]
So it gets called 10 times. And so it's a, it's a tenth of a millisecond slower each time it gets called.

##### **Geohot** [[00:32:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1966)]
I see. So yeah, probably something we have to address. But yeah, the Qualcomm, we shouldn't waste a ton of time on things that are equivalent. The kernels thing is much higher priority than fixing the, than the Qualcomm compiler thing.

##### **Chrism** [[00:32:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1977)]
Yeah. So the kernels thing is down to the fact that I'm using .cast.contiguous.cast. And that's causing the scheduler to output additional kernels.

##### **Geohot** [[00:33:10](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1990)]
Contiguous is real, right? You can't, you can't reorder contiguous or anything like that.

##### **Chrism** [[00:33:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1994)]
Yeah.

##### **Geohot** [[00:33:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1995)]
So why do you need that?

##### **Chrism** [[00:33:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=1998)]
To denote that you're storing as a, like you're, the data is stored as half, but loaded as. A float.

##### **Geohot** [[00:33:27](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2007)]
Yeah. So I would remove the contiguous and figure out how to add a rule to do the graph split in the, in the place where, in the, between the two casts.

##### **Geohot** [[00:33:43](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2023)]
Okay. Right. Like you don't want to use, you don't want to use contiguous for that necessarily.

##### **Chrism** [[00:33:50](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2030)]
Yeah. Yeah. No, for sure. I mean, yeah, I mean, splitting the graph.

##### **Geohot** [[00:33:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2034)]
The thing should be smart enough, right? When it's decided. Right. So this seems like it's going to have to fix, look at derangeify and say like, yeah, if you have like a, you know, a long chain of binary ops and at one part in the chain, it's yeah.

##### **Chrism** [[00:34:13](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2053)]
If you have a long chain of binary ops and at one point in the chain, you, you, you cast and then cast back.

##### **Geohot** [[00:34:18](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2058)]
Yes. If you have a long chain of binary ops, you cast and you cast back. Um, then the split point. Should be before the cast back.

##### **Geohot** [[00:34:30](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2070)]
Yeah. If you cast a smaller detail.

##### **Chenyu** [[00:34:33](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2073)]
You also need to look into why is there like materialization in that chain? Because if you only have cast, then it's not a new kernel.

##### **Chrism** [[00:34:45](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2085)]
That's true. Yeah, that's true. I haven't tried to.

##### **Chenyu** [[00:34:48](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2088)]
It must be like, uh, there's a fork land. Someone also use it then maybe the rules there's a rules to decide the, you know, boundary and you just need to.

##### **Geohot** [[00:34:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2098)]
No, no, no, no, no, no, no, no, no. It's simpler than that. So, so it's basically just like, okay, say you have something like relu cast half cast float, expand jam. Right. I believe currently that that cast float will not go with the gem that cast float will go with the, uh, with the relian.

##### **Chenyu** [[00:35:19](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2119)]
Yeah, probably you put the cost function, but you know,

##### **Geohot** [[00:35:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2123)]
it's not a cost function thing. It's even, it's even stupider than that. Right. Like, because usually the difference is it's kind of like the, normally you don't want to do ops. Like let's say you had a times two, right? You would want to do the times two before you store, because you don't want to do that times to a thousand times, but you don't want to do that times two for everything in the reduced loop, but for casts, you do want to do them. So I don't think you need a cost function. I think you just kind of need, it just should be like binding precedence.

##### **Chenyu** [[00:35:56](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2156)]
Yeah. Yeah. It depends on how many times you expand.

##### **Geohot** [[00:36:02](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2162)]
How many times you expand? It doesn't matter. Basically you want to make casts from smaller things to bigger things like right associative instead of left associative.

##### **Chenyu** [[00:36:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2171)]
Yeah. Makes sense.

##### **Chrism** [[00:36:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2175)]
Well, okay. So the other thing that's worth pointing out is last time we talked about this was, was with regard to the BERT trainer, right? And this does it in the opposite direction where we store. In float and then do the math and half, right?

##### **Chenyu** [[00:36:29](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2189)]
Yeah.

##### **Chrism** [[00:36:29](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2189)]
But it's not, sorry.

##### **Chenyu** [[00:36:34](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2194)]
I think that's a slightly different use case, but it is worth pointing out that it's the

##### **Chrism** [[00:36:39](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2199)]
opposite way around, right? Like the split role there is different.

##### **Geohot** [[00:36:45](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2205)]
You never want to do that. You never want to store in big memory. If BERT's doing that, then it's doing something stupid.

##### **Chrism** [[00:36:52](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2212)]
Maybe I'm, maybe I misunderstood the code then.

##### **Geohot** [[00:36:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2214)]
I'm not sure. So you're saying that the BERT is doing the math.

##### **Nimlgen** [[00:37:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2223)]
Yeah.

##### **Geohot** [[00:37:04](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2224)]
But you store the master weights in FP32 because the, yeah.

##### **Chenyu** [[00:37:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2227)]
So my point is there's no, there's nothing before you are loading weights in flow 32, right? You don't have a chain and decide like where to materialize. You always have your weight in flow 32. Then you do your cast and then do your AOU after that. So it's different here that you have a full chain of stuff and you decide like where to materialize your kernel.

##### **Chrism** [[00:37:33](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2253)]
Yeah.

##### **Geohot** [[00:37:34](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2254)]
Yeah. I mean, if it's already materialized, like I'm not saying that you change the behavior of cast from float to half. I'm just saying you change the behavior of cast from half to float to be right associative.

##### **Chrism** [[00:37:44](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2264)]
Yeah. Yeah. Yeah. I mean, the other thing that's a little bit weird here is that like if you put a like, you know, dot cast half, dot cast float everywhere, like, you know, if that doesn't, if we're going to get to that point, it's not going to get materialized. Like if there's no break between there, then you've like lost precision for no reason.

##### **Geohot** [[00:38:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2285)]
Yeah. That's what, sometimes you might really want to do that. Yeah. That's not, that's not, okay. But yeah, no, the, the top priority here is to get the kernels down.

##### **Geohot** [[00:38:25](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2305)]
down to match the old kernels. If you get down to something where it's the Qualcomm compiler, then we can talk about it. Clearly, we're not there yet. We're three milliseconds off, and the kernels don't match.

##### **Geohot** [[00:38:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2316)]
Yeah, yeah, so that the number of kernels thing.

##### **Chenyu** [[00:38:51](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2331)]
And I think this one, if you believe the issue is with the image memo, then just write a very simple image memo, you should see that.

##### **Geohot** [[00:39:01](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2341)]
Go from here. Sorry?

##### **Chenyu** [[00:39:13](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2353)]
I found the web GPU NAND things, there are still some issue. Oh, yeah. But it's kind of annoying.

##### **Chrism** [[00:39:21](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2361)]
Yeah, I saw this. So it didn't work. I think the thing I saw was.

##### **Chenyu** [[00:39:25](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2365)]
I think that's probably because we decomp the equal. So if we have a special definition for equal, then we'll probably also need that for the equal, because we support both. Get something like that.

##### **Chrism** [[00:39:39](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2379)]
The thing that I fixed was, is NAND? Comparing is also broken with web GPU. So you just have to check manually if you're going to do a comparison of floats. You have to manually check if they're NANDs.

##### **Chenyu** [[00:39:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2394)]
And I mentioned this because this seems to be a natural follow up, just similar to the other one, the three fly back thing can be removed.

##### **Chrism** [[00:40:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2403)]
Oh, yeah. Yeah, I mean, this doesn't really have anything to do with decompositions, but I can definitely just, I mean, it's an easy change.

##### **Geohot** [[00:40:12](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2412)]
Yeah, the web GPU NAND thing, I don't know. I don't care that much about this. Is it just because web GPUs operators don't behave according to any spec? I don't know.

##### **Chrism** [[00:40:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2423)]
Yeah. I mean, for what it's worth, I don't know.

##### **Chenyu** [[00:40:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2424)]
It works on metal. Yeah, my point is we currently have special code to try to handle this, right? So we either don't care at all or try to care more. That's true.

##### **Geohot** [[00:40:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2436)]
Yeah, I think that we shouldn't. I think that the web GPU NAND can just be ignored and just be like, that back end doesn't support that. I don't know. I don't know. I don't like, yeah. Whatever it is now, I'm fine with.

##### **Chenyu** [[00:40:49](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2449)]
Yeah, I think if it's simple, simple as we just redefine, but is NAND and not is NAND, the equal, and if that fix everything, then it's good. We definitely don't want to go crazy and write more stuff.

##### **Chrism** [[00:41:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2465)]
Yeah, I mean, it's not that complicated. If you see it, if you have compare, you just check if either one is NAND.

##### **Chenyu** [[00:41:12](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2472)]
Yeah, so OK. Cool. OK, next is Lama.

##### **Wozeparrot** [[00:41:19](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2479)]
So I have a completed run with optimizer offloading. And there's a current one going. But that's model parallel without optimizer offloading.

##### **Geohot** [[00:41:26](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2486)]
How slow is it?

##### **Geohot** [[00:41:28](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2488)]
So this one, the model parallel one is 8 seconds of step. It's 16. And then the optimizer offloading one is like 5 seconds. Also, yes.

##### **Geohot** [[00:41:45](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2505)]
I mean, I grabbed the optimizer yesterday, that params, that grad clip thing. Because we got to switch to fuse optim, and like proper fuse optim. I also think that like I remember last meeting, we were talking about switching what tensor.cat uses. But I don't even think we have to switch sensor.cat. We just have to switch the optimizer.

##### **Wozeparrot** [[00:42:08](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2528)]
The meeting you said we should switch to sensor.cat.

##### **Geohot** [[00:42:10](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2530)]
I know, I know, I know, I know. But switching the optimizer is fine. What do you mean? Was that the other option last meeting? Yeah. Oh, I didn't understand. My point is we could switch either one, it doesn't matter.

##### **Wozeparrot** [[00:42:21](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2541)]
Oh, cat switching.

##### **Geohot** [[00:42:22](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2542)]
Oh, sorry, if that was the other option... Yeah. We have to basically get fuseoptim to work, because then there should be little penalty for optimals or offslaughting. Is it already not working? I think it's what? It should just work, I think? If it works, what do you mean? Fuseoptim? Yeah. Oh no, a fuseoptim doesn't work because of the cat. The cat is very big. Oh, I see. AMD compiler complained that there's so many brackets, and then if you up the bracket, it segfaults. Wait.

##### **Geohot** [[00:43:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2591)]
Too many brackets can be fixed in a renderer. I actually have a fix for that

##### **Geohot** [[00:43:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2595)]
on a Python renderer. Yes, and then there's also too many brackets. Well, that's a different problem. Yeah, I mean, I don't know. We shouldn't be doing that.

##### **Chenyu** [[00:43:28](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2608)]
But you cannot just split it.

##### **Geohot** [[00:43:35](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2615)]
No, I mean, what you need to do is... So currently we set each gradient to 0. We shouldn't be setting the gradients to 0. We should be setting the gradients to a slice of some big thing that's 0, and then everything becomes an assign.

##### **Geohot** [[00:43:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2637)]
See what I mean? Yes. Yeah, so I mean, that's what it has to become, right?

##### **Geohot** [[00:44:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2643)]
The gradients should not each have their own buffer. The gradient should be assigned to a large gradient buffer. Like set-align-assign.

##### **Chenyu** [[00:44:13](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2653)]
Wouldn't it be nice if O leads fused into a single

##### **Geohot** [[00:44:17](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2657)]
corner or something? But even if it doesn't fuse, I mean, we could at least start by fixing the like... So right now we have something like 0 grad or null grad or something, right? Instead of doing 0 grad or none grad, you want to assign each grad to a slice of a tensor zeros. Like set it. And then when it does

##### **Geohot** [[00:44:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2676)]
plus equals, it'll do the proper assign thing, right? Does this make sense? What's the benefit of this? Because the outputs of the gradients are stored in one big contiguous tensor. This is only good if you want to do gradient accumulation, right? No, it doesn't matter. No, no, it's for fuse-optic.

##### **Chenyu** [[00:45:08](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2708)]
Yeah, that's what I mean.

##### **Geohot** [[00:45:10](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2710)]
Yeah, yeah, yeah. Not for gradient accumulation, but for fuse-optic. So basically like

##### **Chenyu** [[00:45:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2714)]
Basically you want your gradient when it's all ready, you can just work on that giant thing, multiply it by learning rate or something, and work on the full thing instead of split it.

##### **Geohot** [[00:45:26](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2726)]
Yes. In fact, you can even go crazier and assign all your weights like this too. Okay, that makes sense. I think I remember I tried this while I was

##### **Chenyu** [[00:45:41](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2741)]
trying the gradient accumulation thing.

##### **Geohot** [[00:45:44](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2744)]
Yeah, it shouldn't make any difference for gradient accumulation. But it should be one really big gradient tensor that then goes into the optimizer. And instead of each gradient being assigned to a new buffer, all the gradients are just assigned to a slice

##### **Geohot** [[00:46:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2760)]
of a large tensor. Yeah, that's true. Great. That was very okay.

##### **Nimlgen** [[00:46:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2774)]
Okay.

##### **Geohot** [[00:46:19](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2779)]
What do you think we'll get? How are we on RAM for 405? Well, our AP is the same as AMD's. It's not worse. It's worse. Well, they have a couple of the batch size, but they have half the precision. They're actually, I also don't know if they'll optimize their target. At least the run I'm doing right now is optimizing their target as well. Okay. None of this stuff works if it's not fast. We still miss one ASM. Which is the output one. I don't know why. Oh, because the output's sharded? It's a weird shape.

##### **Wozeparrot** [[00:47:17](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2837)]
Like, you shard it across eight, and then the shape is no longer a multiple of the

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2844)]
out size. Oh. Yeah, I don't know. What's the answer? I have no idea. I don't know. Yeah. I don't know. I don't know about this. Autoparallel actually gets more ASM than it does. Autoparallel does? I thought the autoparallel was 100% ASM, Joe. What? There are some things that... Oh. Oh. I'm actually getting out of it.

##### **Nimlgen** [[00:48:12](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2892)]
OK.

##### **Geohot** [[00:48:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2895)]
We'll put the 405e memory somewhere. Use a math to figure out what it is. Just do the node backend. Yeah, yeah.

##### **Chenyu** [[00:48:30](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2910)]
Yeah, just run the node backend to see, is it 10x off, 5x off, 20x off, something like that?

##### **Wozeparrot** [[00:48:38](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2918)]
Hopefully it just fits, and then we don't worry

##### **Geohot** [[00:48:41](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2921)]
about anything. There's no way it would just fit. It won't fit, but I suspect we're going to be 3x off. If it's 3x off, we can think harder about float8. The memory?

##### **Wozeparrot** [[00:49:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2940)]
On church. What exactly does that measure? Because it doesn't seem to line up with the GPU memory allocation.

##### **Chenyu** [[00:49:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2946)]
So this is the other thing. I want to add the peak memory usage.

##### **Geohot** [[00:49:11](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2951)]
I don't exactly know what the main used global counter means. It means it's backwards. Like on all devices? Yes.

##### **Chenyu** [[00:49:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2963)]
It's like the sum of allocated thing, not including the one that's still in ARU cache.

##### **Geohot** [[00:49:30](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2970)]
And not disks.

##### **Geohot** [[00:49:36](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2976)]
I mean, this stuff's all really easy to compute now on the graph. And we'll move the memory planner to the graph. Any thoughts on peak mem usage? Like, I mean, the kind of whole place that I want to move this stuff to is

##### **Geohot** [[00:49:59](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=2999)]
just having one schedule.

##### **Geohot** [[00:50:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3003)]
Or like one. And then if you want peak memory usage, you can just add them all up. I don't know.

##### **Geohot** [[00:50:15](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3015)]
If you want to add to global counters or peak memory usage, by all means, do it. If you want to do it per device, by all means, do that.

##### **Nimlgen** [[00:50:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3024)]
Yeah.

##### **Chenyu** [[00:50:25](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3025)]
I think these things are sometimes you really want it, because otherwise it's very hard to write some test. Then you think about it. Then you forget about it.

##### **Geohot** [[00:50:37](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3037)]
Yeah, yeah, yeah. We could add global counters. Yeah. OK. Does that answer your question? What was for it?

##### **Wozeparrot** [[00:50:47](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3047)]
Oh, because it's still kind of a useless number. Because it doesn't tell you how much is on the GPUs or how much is on the CPU.

##### **Chenyu** [[00:50:53](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3053)]
Yes, that's the per device mem used.

##### **Wozeparrot** [[00:50:56](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3056)]
Per device. Yeah.

##### **Geohot** [[00:50:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3058)]
You know, per device. On the null device.

##### **Nimlgen** [[00:51:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3065)]
OK.

##### **Chenyu** [[00:51:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3065)]
I'll leave it to you to decide how to better write this or figure out a memory.

##### **Geohot** [[00:51:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3074)]
And we can move on to four impromptu. Yeah, so.

##### **Chenyu** [[00:51:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3080)]
And linear schedule.

##### **Geohot** [[00:51:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3084)]
Yeah. So hopefully, my refactor this week goes to this. Yeah. It's good and useful. We're almost finally achieving the dream of it being a single graph rewrite that lowers everything in a pretty sane way. And the JIT will also kind of be free as well. Like, all of tiny JIT's going to be deleted. It's clear what it is now. We're really close to this. So linear schedule is just. Instead of. So like, there's already an op called linear. And this op linear is used in linearization of programs, which just has sources be like the order of all the UOPs in the program. So linearization of schedules is the same thing. It's just all the calls for the different kernels. There's one op called linear. And all the sources are just the calls for the different kernels. And now, things that used to be bespoke code, like. So all of those. Kernels are themselves in the schedule cache with params. But now in order to convert those params back to buffers, it's not bespoke code anymore. It's just a graph rewrite that replaces all the params with buffers. I also added a rule to graph rewrite. Built into graph rewrite to not perverse into the source zero of call. And because you don't want to do this most of the time. Like, you don't want to traverse into the function. If you do want to do this, what you do is you create a rule. A U-pat that matches the call. And then you can call graph rewrite in that rule. And that will create a graph rewrite with a different context. And the reason for this is scope. So like, Paul gives tiny grad scope. And this has been something we've been desperately missing. This is why, like, Lama is so slow. Because nothing is scoped. We put every single op of Lama in a huge graph. And we have a lot of data. And we have no way to specify that there's repeated structure per layer. But the new...

##### **Chenyu** [[00:53:32](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3212)]
That's the deleted... That's the what? That's the removed outer word.

##### **Geohot** [[00:53:39](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3219)]
I removed all the outer world garbage. There's no such thing as an outer world and inner world. They're just nested calls.

##### **Nimlgen** [[00:53:46](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3226)]
Right?

##### **Geohot** [[00:53:47](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3227)]
Right? Like, that's as stupid as trying to write a C compiler where you have, well, you have main. And then main can call functions. And then functions can't call functions. Nope. Everything can call functions now. You can call functions to arbitrary depth. And this will also allow the nesting of jits.

##### **Wozeparrot** [[00:54:02](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3242)]
Oh, great.

##### **Geohot** [[00:54:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3243)]
So, like, think about just jitting a single Lama layer. You'll be able to jit this. And then that Lama layer will not be compiled 24 times. It'll be compiled once. And the parameters will be set correctly.

##### **Geohot** [[00:54:17](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3257)]
The same as the JIT. Oh.

##### **Geohot** [[00:54:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3264)]
Yeah, the other thing about linearization of the schedules is hopefully now, I mean, NivelGen, maybe you can see how we can just do a rewrite rule to rewrite that linear to command buffers.

##### **Geohot** [[00:54:45](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3285)]
Yeah. I mean, I think that's the ultimate dream. Like, the GPU command buffers themselves. It's just a language. Sees the buffers, gets the address of the buffers.

##### **Geohot** [[00:55:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3303)]
Sticks them all in the thing. It's all nicely parameterized. The JIT thing is just a graph rewrite where it replaces the—I mean, we've already done some of this with the synth stuff. But I think we could take it further and actually just build all of the command buffers in basically a renderer for a—you know, whatever, whatever.

##### **Geohot** [[00:55:26](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3326)]
a AMD Mac device. Because that's what it is. Yeah. Yeah, looks good. Cool.

##### **Geohot** [[00:55:43](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3343)]
The other long-term thing I think we should start to... Like, while you're here in Hong Kong, they're the tiny box. I want to be able to... I mean, hopefully... Is there already a way for me to drive the GPU over the network?

##### **Geohot** [[00:56:04](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3364)]
Right now, no. Yeah.

##### **Geohot** [[00:56:07](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3367)]
Yeah, we got to start thinking about how to add that, right? Because I want like a server running on that tiny box. And then I want to be able to target the device.

##### **Geohot** [[00:56:23](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3383)]
But it should be the same.

##### **Geohot** [[00:56:24](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3384)]
Isn't it the same? I haven't really read the Apple stuff, but isn't it the same abstraction as that?

##### **Nimlgen** [[00:56:32](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3392)]
Yeah, it should be absolutely the same abstraction on the turning right side, but yeah, we need

##### **Geohot** [[00:56:38](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3398)]
server. Just encapsulating PCIe? Well, yeah, but wait, what? Where do you want to... We'd have to just run it up and process that. I'd rather not do that. Right? Like, yeah, sure.

##### **Geohot** [[00:57:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3420)]
The server should be able to use USB GPU, right? If this abstraction hierarchy is done correctly, you should be able to run a server on a machine with a USB GPU. And then other things can happen. No, USB 3 is weird. I wouldn't try that. I think that's fine to stay in process. I think there's actually advantages to it staying in process too, because you avoid an extra layer of interaction. Yeah. I want to be able to use GPUs on a remote computer. I want my normal workflow here to be all targeting the RDNA 4 GPU on the tiny box instead of the GPU in my laptop, because the GPU in my laptop crashes. It's terrible. If I could just like...

##### **Geohot** [[00:57:43](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3463)]
Sometimes, yeah. Or if you write a kernel that hangs for over a second, my whole thing goes down. And this isn't anything weird or wrong.

##### **Geohot** [[00:57:54](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3474)]
This is just an empty GPU being grabbed, but you can do the same thing in here. But if the GPU is physically on a different computer, I mean, I'm expecting this to have like no overhead. I'm expecting this to be like USB 4 tier speeds. And I mean, okay, whatever I did over gigabit Ethernet or whatever. A little bit slower, but yeah. I mean, I'm expecting this to be like the normal speed.

##### **Geohot** [[00:58:20](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3500)]
I'm expecting this to be like the normal way to use GPUs.

##### **Nimlgen** [[00:58:32](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3512)]
Yeah.

##### **Geohot** [[00:58:34](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3514)]
And then we think about how to start making these things.

##### **Geohot** [[00:58:37](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3517)]
I mean, this is the other reason that we need to like... You need to just get all of these abstractions perfect, such that when we like lower things to AMD Mech, it becomes easy to broadcast that to... A few years ago, I had a Play Store that was like a thousand computers. All thousand computers are running the server. I could never put a thousand GPUs in one laptop. But I can connect to a thousand TCP sockets and loop through them.

##### **Geohot** [[00:59:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3546)]
That shouldn't even be slow. Should it? What? What's so slow about that?

##### **Nimlgen** [[00:59:14](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3554)]
Yeah.

##### **Geohot** [[00:59:19](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3559)]
Which one? Yeah, do you think the server is going to be like, I think, is the server per GPU, or is the server one for the whole memory space? I think it should be one for the whole memory space. I like that.

##### **Geohot** [[00:59:39](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3579)]
Yeah, it's just like the remote memory, maybe remote direct memory. No.

##### **Geohot** [[00:59:52](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3592)]
OK. We have an RDMA, yeah. Yes. OK.

##### **Geohot** [[01:00:00](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3600)]
We have an RDMA, Danny. How non-custom can we make this? How much can we use this RDMA?

##### **Geohot** [[01:00:06](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3606)]
Is there a real protocol we can use here? It's not quite enough. TCP doesn't support address spaces.

##### **Geohot** [[01:00:16](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3616)]
It can be encapsulated inside of TCP. Yeah, definitely don't want UDP. I don't want my memory accesses to be missed or be out of order.

##### **Geohot** [[01:00:26](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3626)]
DevMemTCP. It goes right to the device. That's DevMemTCP? That's when? 2017. DevMemTCP? You two can work on this. Oh, cool. Oh, I like this. Oh, yeah. We should go. Great. Great.

##### **Chenyu** [[01:00:50](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3650)]
All right. All right. Can you review my change? I think left fixed in EFS.

##### **Nimlgen** [[01:00:56](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3656)]
Yes, I'll review.

##### **Geohot** [[01:00:57](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3657)]
Great.

##### **Chenyu** [[01:00:58](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3658)]
Then I look forward to George, your refactor, to whatever thing he is.

##### **Geohot** [[01:01:03](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3663)]
Yeah, qualify. Yeah, great.

##### **Chenyu** [[01:01:05](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3665)]
Great. OK. Yeah. I think that's it for this meeting. Thank you, everyone.

##### **Geohot** [[01:01:10](https://www.youtube.com/watch?v=W_ZqetFXrK4&t=3670)]
Thank you. Bye-bye. Bye. Bye.
