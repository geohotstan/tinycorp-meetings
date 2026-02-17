# 2026-02-17 Meeting

### Meeting Agenda

**Time:** new meeting #7
- company update
- llama training loop, flash attention
- drivers
- viz / fast gemm
- CALL/PARAMS, assembly
- compiler renderer, image
- lazy assign setitem, scheduler
- other issues and bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=u1TTlOcqeCc)

### Highlights

- **[Meeting Time Change](#geohot-000002)**: Meeting time was moved to better accommodate people in Asia.
- **[Product Teaser: $199 Board](#geohot-000021)**: A first product was teased on Twitter—an affordable ~$199 board, with work in progress.
- **[Llama Loop Speedup via Flash Attention Swap](#wozeparrot-000322)**: Biggest speed win came from switching from their Flash Attention to “HipKittens Flash Attention,” bringing Flash Attention to ~200ms/step.
- **[405B Priority: Build a Plausible Trainer on 8B First](#geohot-000736)**: Focus shifts away from micro-optimizing speed toward getting a 405B step—by enabling model parallel + optimizer offload workflows on 8B first.
- **[Top Sprint Priority: MI350 Stability](#geohot-001101)**: MI350 stability is declared the top priority due to frequent crashes and workflow pain (reboots/discovery signature mismatch).
- **[Escalate to AMD with a Repro Script](#geohot-001304)**: Plan to create a repro/reset script (placed in `extra`) to share with AMD to help diagnose/reset-related breakage.
- **[CALL/PARAMS + Assembly Updates Merged](#geohot-002602)**: Assembly work and the move to the new call API were merged; discussion notes that heavy AI-generated code can become “slop” unless tightly reviewed.
- **[Renderer/Compiler Config Cleanup Plan](#geohot-003208)**: Agreement to remove redundant ways of selecting compilers/renderers; keep backward compatibility via helpers and avoid mixing large code+test updates in one PR.
- **[Image Backend: Progress but Needs Sprint Finish](#geohot-003733)**: Image path improvements (e.g., float16, 2D indexing) landed, but performance still lags image=2; goal is to finish this within the sprint.
- **[Lazy Assign/Setitem Rolled Out + Known Issues](#chenyu-004054)**: Assign/setitem for regular non-disk ops are now lazy; known issues include repeated `+=` behavior and inability to swap two items in one kernel (currently requires workarounds like contiguous/multi-realize).


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=0)]
Okay, welcome everyone.

##### **Geohot** [[00:00:02](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2)]
So we moved meeting to this time. We better accommodate people in Asia.

##### **Chenyu** [[00:00:12](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=12)]
I also didn't randomize the meeting this week because I think it's better to just put all the Lama stuff together.

##### **Geohot** [[00:00:21](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=21)]
We can get started with any company updates. Yes, I mentioned our product on Twitter. We're going to have our first product and it's going to be affordable for people. That was a $200 board? Yeah, $199. We haven't announced what it is yet, but Claude is hard at work on it right now. Okay. Yeah, so I think we'll sell like... I think we'll sell like $1,000 on them at least. But some of this depends on getting... You can get the driver through an Apple. If you listen to the meeting, the product is the Cava Chestnut.

##### **Geohot** [[00:01:17](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=77)]
A very nice EGP board. A USB 3.4, an NDI chip.

##### **Geohot** [[00:01:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=82)]
You can power it with an ATF supply or an ugly 12-volt source. So it should be big enough for people who just don't know anything about outhauling your product! So,��е та н Broadband but the Media Schedule I present to Quimet and that could present these to frigging every razor. Is that gonna be including these new circuits? Not especially. Yeah, so this is nothing extraordinary Catherine.

##### **Geohot** [[00:01:36](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=96)]
I'm investigating about the Ermium from applying and swamping the new lanes on the Jellyfish Road...

##### **Geohot** [[00:01:40](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=100)]
... as you can see with networks. Could you me know a little bit more about that? You can use this microphone. Is that better? Yes. Hi, sweet. OK. That's not. That's not, yeah. OK.

##### **Chenyu** [[00:02:12](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=132)]
Oh, yeah, I saw it was earlier. I think just ask them to create issue. I think that's easier.

##### **Geohot** [[00:02:18](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=138)]
Yeah, for Comma to create issues? Yeah, OK. OK.

##### **Geohot** [[00:02:21](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=141)]
So just create issue first. Otherwise, we don't know that.

##### **Chenyu** [[00:02:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=149)]
Then if we don't have a really good response time guarantee, but we should prioritize that. So we can decide.

##### **Geohot** [[00:02:39](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=159)]
I'm going to just add time. That's good.

##### **Nimlgen** [[00:02:43](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=163)]
Cool.

##### **Geohot** [[00:02:48](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=168)]
Anything else? Or a company update?

##### **Nimlgen** [[00:02:53](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=173)]
No.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=179)]
Next, we're going to start with the current loop. So we're at like eight hours now on Lama 8.

##### **Wozeparrot** [[00:03:11](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=191)]
This thing is like 2x faster than last week.

##### **Chenyu** [[00:03:16](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=196)]
Can you quickly summarize what changed to how much?

##### **Wozeparrot** [[00:03:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=202)]
The biggest change was switching from our Flash Attention to just Hippokines Flash Attention. That drops Flash Attention to 200 milliseconds a step. And the rest of it is jammed.

##### **Geohot** [[00:03:37](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=217)]
I have this really bad cloud-coded script that analyzes step times. I don't know if we want this. Why is the profile one not good?

##### **Nimlgen** [[00:03:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=234)]
Huh? Yeah.

##### **Geohot** [[00:03:56](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=236)]
The profile one? The Viz I have?

##### **Wozeparrot** [[00:04:00](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=240)]
This also reads from the profile pick call. It just breaks it down to what kernel is on what time.

##### **Geohot** [[00:04:10](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=250)]
Yeah, I think it's fine. The tables are the same thing, right? Yeah, it's essentially the same thing. It categorizes the kernels. Yeah, I just wanted it in categories so I can see what's slow.

##### **Nimlgen** [[00:04:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=262)]
OK. So I'm going to go ahead and do this.

##### **Geohot** [[00:04:25](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=265)]
So you have copy.

##### **Geohot** [[00:04:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=269)]
What do you mean by that? You can't just add up the copy.

##### **Wozeparrot** [[00:04:32](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=272)]
It's any copy that's not overlapped with compute.

##### **Geohot** [[00:04:36](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=276)]
OK, nice. Yeah, I see that. Yeah, that's another thing that the generic profiling script can't do. I think it's worth having something like this. But it's important that it uses the same API.

##### **Wozeparrot** [[00:04:49](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=289)]
Yeah, it just reads the profile pick call and then uses that.

##### **Nimlgen** [[00:04:53](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=293)]
Yeah.

##### **Geohot** [[00:04:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=294)]
Yeah. So the headers are mostly, I mean, I see also for all the gems, we are transposing them.

##### **Geohot** [[00:05:04](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=304)]
I haven't looked into that. That might be a question.

##### **Geohot** [[00:05:10](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=310)]
Yeah, I mean, so we can either store the gems transposed or we could find a Asmgem that doesn't need to transpose them.

##### **Geohot** [[00:05:25](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=325)]
So it's really simple to store them transposed.

##### **Wozeparrot** [[00:05:27](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=327)]
At the seed, because storing them for attention, the WQKV stuff, we can't exactly do QKV fully. Just because if we want to shard across the attention heads for 405B, the sharding works out weird, I think, if we just naively store it as WQKV.

##### **Geohot** [[00:05:50](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=350)]
Yeah, I mean, I don't think we should really work on speed too much anymore. I think we're pretty good on speed. I think now the main thing just has to be getting a 405B step.

##### **Geohot** [[00:05:59](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=359)]
Yeah.

##### **Wozeparrot** [[00:06:08](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=368)]
Yeah, I need to still test model parallel. But I think it should just work. I don't see many blockers as long as we, and I think everything fits too. Oh, fuseOptim doesn't work.

##### **Geohot** [[00:06:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=382)]
Yeah. I'm not surprised. I mean, probably what we want to do is just not use the optimizer class and just manually do it in the trainer.

##### **Wozeparrot** [[00:06:32](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=392)]
The problem with fuseOptim is that when we create, it uses cat to create the fused grads and fused parameters. Yeah. And that one cat kernel is extremely large. And it's been like .

##### **Chenyu** [[00:06:47](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=407)]
Do you want to try the new set item fused? Oh, fused into one kernel.

##### **Wozeparrot** [[00:06:53](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=413)]
I will try the set item fused. I'll try rewriting it until you set it. And that was one of my thoughts too.

##### **Chenyu** [[00:06:58](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=418)]
I think it works if it's not overlap. There might be subtle issues, but I think let's refuse into one kernel.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=427)]
OK. Because I do want to look into it.

##### **Wozeparrot** [[00:07:11](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=431)]
Yeah. OK. Ideally, we want to do grad clipping as part of the optimizer. So I have a PR that moves grad clipping to also use the fused tensor. And that saves a bunch of things.

##### **Geohot** [[00:07:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=442)]
So I'm going to try to get rid of the small kernels. Because basically, all the small kernels are part of grad clipping in the optimizer. Yeah. Yeah.

##### **Geohot** [[00:07:36](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=456)]
I mean, I think maybe even before 405B, what we want to do is we want to get a 405B plausible trainer running for 8B. So we want to get model parallel and optimizer offloading working on 8B.

##### **Nimlgen** [[00:07:59](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=479)]
I think it's a good thing. Yeah.

##### **Geohot** [[00:08:01](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=481)]
I think I think it's a great idea. Yeah, I think Flash attention is done.

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=484)]
Jam is done. I'm happy with the state of those. I don't think we have to keep messing with them.

##### **Wozeparrot** [[00:08:09](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=489)]
I'll do a run with parameterized jam just to make sure nothing's broken.

##### **Geohot** [[00:08:14](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=494)]
Yeah. So I'm testing it right now. We used to have, the only difference between parameterized jam and the current jam is that the parameterized jam is the way the parameterized jam looks. It looks like the embedding gems are using Asmgem, and that might have been what made it unstable.

##### **Geohot** [[00:08:33](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=513)]
So I added a low. It's unstable.

##### **Geohot** [[00:08:39](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=519)]
It's not just slow. It's actually faster. I see. But I think, or I don't know. It could also be just tiny AMD4, but we also really have to do something about these discovery signature mismatches. It's super annoying for the workflow.

##### **Wozeparrot** [[00:08:55](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=535)]
So on my branch, I added some contiguous and contiguous backward, and it seems that there was some weird fusion with a gem and an RMS norm that was being weird.

##### **Geohot** [[00:09:07](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=547)]
Oh, OK. No, it just, on tiny AMD4, it just crashed again. It has nothing to do with the big gems.

##### **Geohot** [[00:09:24](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=564)]
Yeah, I don't know. Yeah, try a run with your setup with the... Yeah, do a run on the three.

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=574)]
Yeah, and if it's unstable, we should just figure out exactly which kernels got changed. But yeah, I mean, we need more stability here. There is no bad kernel that needs a reboot in the system.

##### **Wozeparrot** [[00:09:52](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=592)]
Yeah, for, I guess, slightly moving on to drivers, the discovery signature thing has been kind of annoying. It's annoying enough that when I'm doing single kernel testing, I just switch to AMD GPU. Yeah. Because at least on AMD GPU, the reset is, the cycle time is just a lot faster. I don't have to hive reset each time.

##### **Geohot** [[00:10:19](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=619)]
Yeah, NimbleJet, how are they doing that? So, AMD GPU doesn't do hive reset.

##### **Nimlgen** [[00:10:34](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=634)]
Basically, yeah, the problem is that we cannot sync a QLQ after that. And because they use, like, something like mass that works for them.

##### **Geohot** [[00:10:49](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=649)]
I see. Can we enable that?

##### **Nimlgen** [[00:10:56](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=656)]
Yeah.

##### **Geohot** [[00:10:56](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=656)]
We can. Yeah.

##### **Geohot** [[00:11:01](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=661)]
I mean, we have to, like, absolute top priority of this sprint is getting this stuff to be stable. It's a super frustrating workflow.

##### **Geohot** [[00:11:13](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=673)]
Yeah, I see.

##### **Nimlgen** [[00:11:15](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=675)]
So, actually, I have no idea how, like, my 350 machines got into this discovery mismatch state. I mean, I think it's just a matter of testing the data,

##### **Geohot** [[00:11:23](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=683)]
and actually, it happens, like, it happens to me all the time. Like, it's not like I get it in some weird thing.

##### **Nimlgen** [[00:11:32](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=692)]
Yeah. Yeah. I mean, I have Pfizer, so it worked fine on MI300, but not MI350. And actually, after that, the GPU won't respond. Like, you can bypass this, like, actually, for some reason, like, the table is clobbered. Yeah. So, that's why we have signature mismatches. And after, and actually, this table is, like, located after TMR zone. So, I don't know if it's something related to SOS, because, like, even if you just hard-coded all the registers and all that stuff, so either bootloader or SOS won't respond to the SMU reset. And I know, yeah, it's pretty reproducible. I'll take a look into that. But actually, the AMD GPU, like, if you do the HIFR reset in a loop, so it will, like, last for, like, six times or so, and they will have the same problem with the bootloader not responding.

##### **Geohot** [[00:12:38](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=758)]
Oh, even just looping HIFR reset eventually breaks? I mean, with AMD GPU, yeah.

##### **Geohot** [[00:12:47](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=767)]
I mean, we have to be doing something wrong, right? Yeah. Like, you don't think these things are just this bad.

##### **Nimlgen** [[00:12:55](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=775)]
I mean, with AMD GPU, I use their reset, like, the AMD GPU reset function.

##### **Geohot** [[00:13:04](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=784)]
And it also breaks for them. Ugh. Um, we, like, is there, like, a repro script to do that that we can send to AMD?

##### **Geohot** [[00:13:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=800)]
Yeah. I mean, it's, uh, yeah, I mean, it's... Yeah, just add a script, and I'll link it on Twitter for AMD and be like...

##### **Nimlgen** [[00:13:30](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=810)]
So that one, I mean, AMD hardware, so you just do reset. If you use, like, their tool to do reset.

##### **Geohot** [[00:13:38](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=818)]
Yeah, I mean, like, the CSFS to do reset.

##### **Geohot** [[00:13:45](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=825)]
Yeah, just put a script in extra that will bring down a machine that has, like, a lot of stuff. And then, like, the kernel driver, and the latest firmware.

##### **Geohot** [[00:13:53](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=833)]
And then we'll report it to AMD. Yeah.

##### **Geohot** [[00:14:03](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=843)]
But, yeah, no, I mean, we need, we need some way to mitigate this. We need... Because it's, I mean, it's super frustrating to work with.

##### **Geohot** [[00:14:14](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=854)]
Yeah, I see. Yeah. So, highest priority of this sprint is... Yeah. Improving the stability of the MI350 stuff. Yeah, I mean, I just got another... Like, my WAN DB runs are all crashing on tiny AMD 4.

##### **Geohot** [[00:14:44](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=884)]
And I don't know if this is a change I made with the gem stuff. Yeah. Or if it's... I don't think it's a change I made with the gem stuff. The tests pass. Like, I test all the kernels that LAMA uses.

##### **Geohot** [[00:14:59](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=899)]
And the loss seems correct. Yeah. I'll take a look into this. All right, cool.

##### **Nimlgen** [[00:15:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=920)]
So, yeah, also, I think this sprint, I'm going to look into the beam timing stability. Actually, I've been looking into that. So, this week as well. And actually... So, no, I'm not sure that's related to the cache. And I had the other theory that it's related to the clocks or something like that. Because if you run... Yeah. Like, after some time, like it takes to compile kernel, you just run the... Like, the first kernel is always... In my test, it was always faster than others. Yeah, I mean... Actually, yeah. I mean, the difference, like in terms of percent, you've seen on tiny F1, is huge. I mean, on our, like, R4 machines, it's not so bad. But it's about 30% .

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=983)]
We probably want to have stable STD for beam timings

##### **Geohot** [[00:16:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=989)]
if we're using the AM driver. Yeah.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=997)]
But again, this is all much lower priority than making the MI350 stable. I just hit again. The thing crashed, and now I'm getting discovery signature mismatch, and I have no choice but to reboot the whole machine. It takes like five minutes.

##### **Geohot** [[00:16:58](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1018)]
And yeah, any way you can reproduce this using AMD's tools that we can send to AMD, they're very responsive. OK, yeah. We'll listen to scripts. We'll see what happens. OK, anything else for a wasp parrot? That's all. OK, anything else for an Imogen? That's it. I know.

##### **Nimlgen** [[00:17:43](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1063)]
We can only discuss if we want to see like PMC, like, the actual performance.

##### **Geohot** [[00:17:47](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1067)]
Like, metrics for NB. I think lower priority than ability and beam.

##### **Geohot** [[00:17:58](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1078)]
But yeah, we still got to go work on the SQTT-like thing.

##### **Geohot** [[00:18:08](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1088)]
What's it called? EMA. EMA? Yeah.

##### **Nimlgen** [[00:18:16](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1096)]
Performance monitor something.

##### **Geohot** [[00:18:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1100)]
Cool. And again, I think we should really focus on the 250X. But I did get that working on my 5060 for USB4. And yeah, I mean, I think that what we have to do is just, like, the timestamps are implicit. It's sampled at a fixed frequency. So we'll just put that on a viz with the, you know, the timestamps at a fixed frequency, one per thing.

##### **Geohot** [[00:18:51](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1131)]
And then we can kind of see what the waves are doing. Yeah. I believe that's 32 cycles or so. And that should be configurable. Oh, we can sample faster. I think we do the fastest. But. Yeah, that should be configurable.

##### **Geohot** [[00:19:19](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1159)]
Yeah. And for any sort of, like, performance counters, I mean, what I really want from them is just, like, we have to think about what we can put in viz equals 1 and what we can put in viz equals 2. If we can put performance counters in viz equals 1, they're, like, valuable. We can, like, always run them. If we have to put them in viz equals 2, then, like, we're already running the whole tracer

##### **Geohot** [[00:19:40](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1180)]
and everything. Yeah. Yeah. So, yeah. Yeah.

##### **Geohot** [[00:19:52](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1192)]
Top priority, MI350x stability. I think everyone here is frustrated with having to reboot the thing. And I would imagine that most of it isn't anything you're doing. It might even be stuff AMD is doing. So anything that we can send to AMD, publicly shame them about, you know,

##### **Geohot** [[00:20:16](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1216)]
it's always effective. Sounds good. Thanks for the viz question. I don't know. I don't think I'm broadcasting. If you want to talk. I'm sorry. I'm on the computer. I can talk. So for ASM, the thing is still not. Can you get closer to the mic? Hang on. It's not that fast for the living one. I think it gets, like, 600 terabytes a month for a beta port. That's unstable. It's definitely faster. I got the thing. I don't think the instability is related to it. The embedding kernel is faster. At least the whole thing is. It goes from 17.5% MFU to 18. I don't think they can hear you. Can you talk through that? Yeah. Okay.

##### **Nimlgen** [[00:21:43](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1303)]
So, yeah. So, yeah.

##### **Geohot** [[00:21:48](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1308)]
I'm past your step count now.

##### **Wozeparrot** [[00:21:51](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1311)]
I'm at like 120 steps, and it's been stable.

##### **Geohot** [[00:21:56](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1316)]
I see one of mine made it to 120. But, yeah, I mean, this might literally just be AMD 4.

##### **Geohot** [[00:22:03](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1323)]
I don't know if we've ever done a training run. I did hit a 25% MFU though. 25? So it's more. This is PS8 with GraticuMF2. Yeah, but you're getting 25. That's the highest we've seen. Yep. Great. Yeah, no, it should be faster. Yeah, yeah, yeah. I mean, my tests show that it was faster.

##### **Nimlgen** [[00:22:28](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1348)]
Yeah. So, yeah. So, yeah. So, yeah.

##### **Geohot** [[00:22:45](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1365)]
So, I think that's pretty good. Anything else for this Cache Gem or whatever you will be working on next week? I don't think your mikes working. No, we'll have to get a mic. We'll get a mic for the office. So you two are in the same room? Yeah, we're in the same room. But I know we have a much bigger room. Yeah, yeah. It's super nice. We got carpet now here. I'll post a picture. Oh, but yeah, I'll talk and see if you can you can fix it. I think it's not working. So

##### **Nimlgen** [[00:24:08](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1448)]
yeah,

##### **Geohot** [[00:24:27](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1467)]
it's not working. Is it working? I think you also have the SDMA so it's like this. Oh, okay. Now it works. Yeah, we'll get we'll get a real audio setup. We're in here. Yeah, we got fiber internet coming too. Oh, there's no fiber internet? Not yet.

##### **Geohot** [[00:25:10](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1510)]
Not yet. We're on one 5G.

##### **Chenyu** [[00:25:13](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1513)]
I see.

##### **Geohot** [[00:25:14](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1514)]
Okay. That's a way to sign the fiber internet with the company CHOP.

##### **Chenyu** [[00:25:21](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1521)]
All the stamp?

##### **Geohot** [[00:25:23](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1523)]
Stamp. Yeah, yeah, yeah. We have an official stamp. I had to go pick it up. I mean, overall, it's been easy. Everything's been good. It was very easy to sign a lease and the internet was easy.

##### **Geohot** [[00:25:38](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1538)]
Hey, guys, it's Juwan. Congrats on the new office. Go check it out. Hey, thanks. Okay.

##### **Chenyu** [[00:25:51](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1551)]
Assuming there's no fast chem other stuff, we can move on to the corporate ROMs, other assembly stuff.

##### **Geohot** [[00:26:00](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1560)]
Cool.

##### **Geohot** [[00:26:02](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1562)]
Yeah, so I got I got the assembly stuff merged. I left the emulator in tests. But the stuff that I did merge, I think, like, kinda meets the bar for tiny-grass марq. Most of it is handwritten, almost none of it's Claude. I mean, Claude did like 10 lines, the same way I used to use it. I've started to think that the AIs are just scarily like a slot machine. Like you just type something and you hope it will work. And the problem is it does work like one of the 10 times, and you get addicted to that variable reward. But it's not really a good workflow to accomplish anything. So yeah, I moved all the emulator crap out and just have the ESL, the generator in there. That's all merged. Call param, everything's moved to the new call API. It's pretty nice. It's pretty easy to see. You can do custom kernels and non-custom kernels, or you can do custom kernels and non-custom kernels. All using the same API. Yeah, I reviewed the x86 assembly backend. There's good stuff in there, but like if Thompson doesn't want to, you know, I'm not going to have arguments about ways to do things. Like if he doesn't want to do it the way that, you know, I want it done and he's not going to maintain it, I'm going to maintain it.

##### **Geohot** [[00:27:28](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1648)]
So that's my take on that. And yeah, so this week I want to work on

##### **Geohot** [[00:27:38](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1658)]
two things. I want to work on starting to think about what it's going to take to move Flash Attention and Gem into our Code Gem path. I've been thinking a lot about like producers and consumers. I'll read over the tiny kitten stuff and figure out why it doesn't match hip kittens and like sort of what primitives we need. And I also want the trainer to start faster. I don't know. It's not too bad now. I made some improvements to it. So it looks like it starts in like five minutes. Does a step in like 90 seconds. Like it's okay. It's usable. Hopefully that's not too bad for 405B. Do we know how many more layers is 405B versus eight?

##### **Geohot** [[00:28:35](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1715)]
Not sure. We're going to be like, it's 126 layers. It is 32. And what's the other one? 32. Okay. So it's like 4x lower. Oh, kind of doable. Yeah, I'm gonna look into that too this week to see if I can actually get called to collapse all the layers.

##### **Nimlgen** [[00:29:18](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1758)]
Okay. Anybody contains was B. Likeuta alias çin

##### **Geohot** [[00:29:30](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1770)]
Come on up.

##### **Chenyu** [[00:29:39](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1779)]
Next is the compiler, renderer, and image.

##### **Chrism** [[00:29:44](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1784)]
Yeah. Yeah, so compiler pairs is removed. I have a PR up to remove compiler set as well and unify. The big thing there is unifying all the renderers under a single initialization API, so you aren't passing some of them some arguments and some other arguments. It's pretty opinionated, so I don't know. I'd be interested to hear what people think about that. But basically, you would pass a string that is interpreted as the architecture. So for instance, maybe it's a GFX 950 or GFX 1100 or whatever on AMD. But then on Android. If you're on CUDA, you would pass SM underscore 120 or SM underscore 89 or whatever. And I think most stuff seems to fall into this category pretty well because as it turns out, it's pretty useful to have a human readable string to define your architecture. So for the most part, everything seems to fit into that pretty neatly. So that was the thing I was thinking of going for refactoring renderers.

##### **Chenyu** [[00:31:06](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1866)]
Are we going to remove all the variant of context bar or the helper bars?

##### **Chrism** [[00:31:13](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1873)]
Yes. The idea was, and I'm certainly open to other ideas here, but it feels very odd that we have two different ways to select which compiler. So for instance, you can both do AMD CC equals LLVM, but then you can also do AMD LLVM equals 1. And I feel like we should just have one of these, that we shouldn't have both often.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1896)]
So we should definitely remove that. I agree.

##### **Chrism** [[00:31:39](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1899)]
Yeah.

##### **Chenyu** [[00:31:40](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1900)]
So my... So we currently have the same thing for device, right? It's like CPU equals 1 and then equals to CPU. I think we should at least have something like a renderer equals to something. And maybe it's discoverable through the Python dash and device thing.

##### **Chrism** [[00:31:59](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1919)]
Yeah, exactly. I think renderer is probably a little bit too long of a name, but something like that. Yeah. Is definitely not a bad idea.

##### **Geohot** [[00:32:08](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1928)]
Well, but yeah, so I wouldn't like... I'm looking at this PR. I mean, I wouldn't break the old behavior. I would just move the old behavior into helpers, right? Like I think that we don't want... I agree that there's two ways to set the renderer and that's annoying, but the idea shouldn't be to change tons and tons and tons of stuff. It should just be to just put a minimum bridge in helpers that reads for the old ones. Yeah, okay. And then sets the new ones. And then you can change everything else to use the new one. Yeah. So you don't have to change. I mean, when I look at this PR, the problem I see with it is that it's updating both tests and the code at the same time. And you should avoid doing that as much as possible.

##### **Nimlgen** [[00:32:48](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1968)]
Yeah.

##### **Chrism** [[00:32:49](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1969)]
No, that makes sense. Yeah. No, I think that's probably the right way to do it.

##### **Geohot** [[00:32:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1974)]
Yeah, but no, no. In general, I'm pro removing it and making it something like CPUCC. And as much as we still have CPU equals one, AMD equals one, we may want to go to just dev.

##### **Geohot** [[00:33:08](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1988)]
Yeah.

##### **Geohot** [[00:33:09](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1989)]
But that's that should be that's like such an opinionated change that that should be a one line change. Right. The more opinionated the changes, the smaller the diff should be.

##### **Chrism** [[00:33:18](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=1998)]
Yeah. Yeah, that makes sense. Yeah. Yeah. Um, the other stuff that was in there, which I think is also pretty opinionated is changing, like how null and the Python backend work, which is like the idea being like, you would set your renderer and your architecture to determine like you use these two things to set what you're emulating or what you're using your null backend for. And in theory, this allows you to run your null backend on everything, as opposed to just like the two things that we have hardcoded support for. So the idea being that you could set like your your arc via a context bar, and you could say, okay, well, you know, I want to, you know, compile for a 5090 or if I want to compile for a 4090. I mean, obviously can't run it, but it can, you know, you can run the compiler stage. Yeah.

##### **Geohot** [[00:34:11](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2051)]
I mean, yeah, so I see what you're doing there with the with the renderers are just stripping the name renderer off it. I like that. Um,

##### **Geohot** [[00:34:21](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2061)]
but the Yeah, okay, so you just you just code all of them in there.

##### **Geohot** [[00:34:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2069)]
How was the arch specified? We had a car.

##### **Chrism** [[00:34:33](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2073)]
Yeah, there's a context for called cross arch. And then you would set that. I mean, it can be named anything, but you set that and then it specifies the arch.

##### **Geohot** [[00:34:41](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2081)]
I mean, in some ways, we kind of want to put that like on the device. Right? Like we want that to be on the when it's doing the lowering. Right? When it's doing the the creation, we have a kernel you up and you're creating the the the source you up in the binary you up. It needs to know the arch. Yeah. So I mean, yeah, I see like, you have something here like no CC dot value is not Qualcomm colon IR three.

##### **Geohot** [[00:35:11](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2111)]
Yeah, yeah, yeah, yeah, that's the that was the syntax.

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2117)]
But what is that the syntax of?

##### **Chrism** [[00:35:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2120)]
That's so that's for the the like the renderer. So you're specifying that I want the Qualcomm IR three renderer. And then it's additionally set cross arch equals. 630.

##### **Geohot** [[00:35:32](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2132)]
Can you can you can you write this up in an issue? And then we can debate it there.

##### **Chrism** [[00:35:35](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2135)]
Yeah, for sure. That I think it makes sense.

##### **Geohot** [[00:35:38](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2138)]
That's good. But yeah, no, as far as the the the other change goes, yeah, just move the move the environment variable wrangling into helpers. Yeah. And that way you can update the code without having the tests. Yeah.

##### **Chrism** [[00:35:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2154)]
Yeah. That bug with type supported, we hope we will help you remove but that there are bugs that are there. We don't have any bugs that are related to this. Sounds good. Yeah. And then what else? So the other stuff is image equals one. Yeah. So so we have float 16 support now and that was like a 10% improvement. But then a bigger thing was was getting a 2D indexing to actually work. I still need to work out a little bit. I think. I think that I'm not being able to, right now the way I'm doing it, it doesn't look like I'm removing enough of the simplified valid stuff. Like it would be nice if there was less gating. But I am doing the thing where we pass multiple textures in case there's two different things that we need to do to modify, or to be able to remove some gates. So that's good. It's not fast enough to replace image equals two by default yet, though. I just merged this. Oh, okay, you got it merged. Do you know all the stuff that's missing? So I haven't figured out exactly what... There's a lot of differences in terms of what kernels get generated. I haven't been able to figure out exactly what is causing the performance. But my intuition is that it has to do mostly with not being able to remove as many gates as I would want to be able to. But I need to look into that more.

##### **Geohot** [[00:37:33](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2253)]
Okay, yeah, sounds good. I mean, yeah, I really want this done, this sprint. This has dragged on way too long. I think this is... Yeah, the compiler stuff is a lower priority than this. I think this is the highest priority.

##### **Geohot** [[00:37:44](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2264)]
For sure. Yeah, no, this is...

##### **Geohot** [[00:37:49](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2269)]
Yeah, this has now been... Now, I'm not sure. We're now over eight weeks into this. I expected it to kind of be a one or two sprint thing. Okay, sounds good. Yeah, and then, yeah, put an issue up for how to discuss the opinion of the change. I agree that the current story around this stuff is pretty nonsensical. And yeah, I mean, not because of anything you did, but just like we never really have decided, okay, like, what are the actual things we're choosing? I think maybe we may want it to look like the LLVM3. And then, like, I'm going to try and triple as much as possible. Yeah, yeah. That's not where I was thinking.

##### **Chrism** [[00:38:25](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2305)]
Like, I thought, oh, maybe it was called target or something like that. But that seems like the sort of environment variable that someone else might want to use.

##### **Geohot** [[00:38:33](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2313)]
Yeah, I mean, it's not a question as much of what we name the environment variable as like where we have that state. Yeah, yeah. And I kind of like the idea of putting that state like on the device you op. Like the device you op can have a... There's multiple things that are conflated, right? Like you have a device. You have an arch. The device has a number. And the device can also be like a cross device, like the null thing. Yeah, yeah. So you kind of have your... You have your runtime device, your compilation device, your renderer, and then your device number, which is part of the runtime device.

##### **Chrism** [[00:39:10](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2350)]
And also mock GPU, which is not well specified.

##### **Geohot** [[00:39:16](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2356)]
Well, yeah. So yeah, the mock GPU changes your runtime device more than it changes...

##### **Geohot** [[00:39:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2362)]
Yeah, yeah.

##### **Geohot** [[00:39:24](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2364)]
Yeah. I mean, that's more of a flag to the runtime device. I think actually the mock GPU thing isn't the worst. But I think it's...

##### **Geohot** [[00:39:34](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2374)]
It does make you render to PTX on CUDA. Yeah, I mean, that's true.

##### **Geohot** [[00:39:42](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2382)]
But I mean, that's not a... Like what I would do for that is kind of just have an assertion.

##### **Geohot** [[00:39:48](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2388)]
Yeah.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2390)]
Oh, it makes you render to PTX. I see. Yeah. I don't know. But yeah. Yeah. This is the kind of thing that needs to be discussed in an issue when we come up with a good way to do it. But yeah, no. Overall, I like most of the compiler set thing. I like the dictionary a lot better than compiler set. Just have the default one be the null string.

##### **Geohot** [[00:40:09](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2409)]
Yeah. I think that's it. Oh, I just remember... Do we want to do anything for multi-machine? Yeah. I think we should. What would we do? I don't know. Half of the milestone is multi-machine.

##### **Geohot** [[00:40:37](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2437)]
Yeah. I think we have enough to deal with right now that's not multi-machine. Yeah, that makes sense. Hopefully, we can get to it in March. But yeah, I don't think we should put any resources on multi-machine right now.

##### **Nimlgen** [[00:40:51](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2451)]
Yeah.

##### **Chenyu** [[00:40:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2454)]
Next is my stuff. So the most important thing is assign and set item for regular non-disk thing are lazy now.

##### **Nimlgen** [[00:41:09](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2469)]
Right.

##### **Chenyu** [[00:41:10](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2470)]
You can try it. Let me know if you see any issue. Currently, there are two known issues that I'm aware of. And one... I'm currently fixing is... You can see my test earlier. If you do a plus equals to for multiple times, it will change the buffer. I know the reason for that. Fix that. The other one is if you want to do like a swap two items on one kernel. For now, we don't have the way to write that. So we can add the contiguous somewhere to make it correct. Yeah. But for now, I don't know how to like use that into one kernel. It's probably fine. But if we want to do something like sort in one kernel, then you need to have a swap mechanism. Yeah. Currently, this is done through like tracking the dependency and push everything into the realize and do like multiple schedule and kind of a multi-schedule. So it's like multiple realize there. The eventual goal of this is to push that into actors. But I just discovered tons of bugs in the current actor behavior. It's really... Yeah.

##### **Geohot** [[00:42:36](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2556)]
So I really don't like that it's still multiple realizes.

##### **Chenyu** [[00:42:41](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2561)]
Yeah. I don't either. And then there's also... This is good too. This is good so that I can separate issues. Because now I see what a structure needs to be, then I can start to see why it's like broken. Sometimes some kernel just drop. I think it's the biggest issue. It's probably not built on the good assigned behavior anyway. So I really want to fix that.

##### **Geohot** [[00:43:14](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2594)]
Yeah. No, I mean, I think it's a fine intermediate. I'd rather like... I'd much rather push any sort of complexity into the realize function instead of having the complexity be in things like set item.

##### **Nimlgen** [[00:43:27](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2607)]
Yeah.

##### **Chenyu** [[00:43:28](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2608)]
So my strategy now is... This is what cloud is really useful for. I just have cloud fuzz all kinds of front end that you can think of to abuse the set item and see like what's correct and what's wrong. So now I'm pretty confident, but still let me know if you see anything that's like wrong.

##### **Nimlgen** [[00:43:47](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2627)]
Okay.

##### **Chenyu** [[00:43:49](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2629)]
Do you want to switch cat to use that instead? I'm sure I can test that.

##### **Geohot** [[00:43:56](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2636)]
Yeah. I think that we don't need to switch it like in the fuse assign, even if we put it behind an environment. Well, for now we can have something called like set item cat or something.

##### **Chenyu** [[00:44:08](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2648)]
Okay. I will test. I need to better test that. There are some subtleties when you repeatedly set to a same buffer. But got a pretty good handle on that.

##### **Nimlgen** [[00:44:19](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2659)]
So.

##### **Geohot** [[00:44:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2660)]
Yeah. I mean, I do want to switch it to after behavior too. Like, I'm not sure, does it really not work? Like, are there bugs in the current after? Yes.

##### **Chenyu** [[00:44:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2669)]
It has tons of bugs. I don't even know how it works. It doesn't make sense.

##### **Geohot** [[00:44:36](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2676)]
I mean, it makes less sense in the... Okay. So I'll explain the...

##### **Chenyu** [[00:44:42](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2682)]
I think it's probably just a combination of some tags or bufferize. But I think it's probably just a combination of some tags or bufferize. You know, right? Wouldn't that just drop something subtlety? Well, I can explain to itself, it's kind simple.

##### **Geohot** [[00:44:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2694)]
I can explain the spec for after. Because after has a very clear spec.

##### **Chenyu** [[00:44:59](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2699)]
But then there is... Absolutely. After is correct. It's how the after is being handled generates the wrong kernel. And sometimes it just drop kernels.

##### **Geohot** [[00:45:12](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2712)]
Yeah, I mean, it's not really designed to be in the kernel graph. That's not really tested. Oh, yes.

##### **Chenyu** [[00:45:17](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2717)]
So that's the main issue.

##### **Geohot** [[00:45:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2720)]
Yeah. The design for the spec of after, and this is another problem potentially with assign. So I think one of the issues with assign is that you can have assigns to non-realized buffers. And then what do you do?

##### **Geohot** [[00:45:35](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2735)]
A full assign or a slice assign? Either one. Uh... No, we just find a place, create a contiguous word. You just add a contiguous. So the spec of after

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2762)]
is that after belongs on a buffer, and then you can put anything you want on the other sources. So the first source to after is a buffer. You can put anything you want on the other sources. And then after promises that you will get that buffer after the stuff in the other sources has run.

##### **Chenyu** [[00:46:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2780)]
Yeah, so this immediately is wrong

##### **Geohot** [[00:46:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2782)]
if you have a self-dependency. What's a self-dependency?

##### **Chenyu** [[00:46:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2789)]
You cannot have a buffer that has after to itself, right?

##### **Geohot** [[00:46:35](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2795)]
Well, no. So if you want to do this with a slice assign, it's not that the buffer has after to itself. It's that the after becomes the uop on the tensor.

##### **Geohot** [[00:46:51](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2811)]
Right?

##### **Geohot** [[00:46:51](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2811)]
So what you would do is you'd traverse the tensor graph, and you'd update the base tensor to be the after. Yes.

##### **Geohot** [[00:47:01](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2821)]
It should work.

##### **Chenyu** [[00:47:03](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2823)]
That's the first thing I try, and I struggle with that. Why? I don't know.

##### **Geohot** [[00:47:11](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2831)]
It's just silently wrong. I see. Okay. I mean, it's not tested.

##### **Chenyu** [[00:47:20](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2840)]
I mean, I understand. I also want that to work. That seems to be the most obvious way to deal with this.

##### **Geohot** [[00:47:27](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2847)]
Yeah. Yeah. It might be weird on the range of high stuff or something.

##### **Chenyu** [[00:47:35](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2855)]
So I clean up a lot of buffer related helpers and the assigned related thing in render file. So everything is at least. Yeah. So you're. Or what it should be. I think so. You clean up a few up. That was nice. I really want to change. This might be an API change, but I really want to change is realized. I think is realized should be in should always be true. Once you call realize on something. It's very weird. Let's if it's not, it's realized then what it is. It probably describe a subset of state, but it's. It's weird.

##### **Geohot** [[00:48:19](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2899)]
I'm very supportive of changing it. It's not really thought through. It's not an external API.

##### **Chenyu** [[00:48:25](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2905)]
The main issue I hit and this happened in a lot of tests we wrote is empty. Empty is a very weird thing that if you call realize on an empty, it does nothing. Just like const. Only if you do something to an empty, say plus one, and it would. Yeah.

##### **Nimlgen** [[00:48:46](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2926)]
Yeah. Yeah.

##### **Chenyu** [[00:48:46](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2926)]
Presumably give you a like allocate a buffer for you. And this behavior is very weird because we use empty or all kinds of tests in like schedule and like how many kernels and that always is the only thing that behaves differently.

##### **Geohot** [[00:49:04](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2944)]
Yeah. So I think the solution there might be to just, I wouldn't change what empty actually does, but I think empty is just always realized.

##### **Chenyu** [[00:49:11](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2951)]
Oh yeah. So that's what I want to change. So similar to const, I want to basically, I just want. To follow that invariance because then I can use a lot of is realized in the tensor.py instead of now I need to look into the UOP and check if it's app.buffer or something like that.

##### **Geohot** [[00:49:27](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2967)]
Yeah. I think that's a good invariant.

##### **Geohot** [[00:49:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2969)]
Yeah.

##### **Chenyu** [[00:49:31](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2971)]
So let's another thing I want to fix is the copy and no op. Uh, we currently have like three hacks that depends on no op. And I think that's really mad.

##### **Geohot** [[00:49:42](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2982)]
I, we should delete no op. No op is no op is just asking for problems.

##### **Chenyu** [[00:49:47](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2987)]
Uh, sure. But we, we first need to, so for now it's very similar. I know the copy one.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2994)]
Yeah.

##### **Chenyu** [[00:49:54](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=2994)]
For now it's the same as forcery shape. Like yeah. Designed for something else. So, uh, I think no op has issue with copy. Uh, this might cause the issue in the weird behavior in multi. I I'm pretty sure in some cases it will just do a random copy because. No op is not the do properly or something like that. Uh, so let me know if you find anything weird in the, in the trainer that I think you think is a schedule issue. I would take a look. I, I want to get this fix because copy, uh, to do a lazy, uh, disc, uh, disc assign. That was the very first goal when I started this project, uh, it's, we need to rewrite that to copy. And for now copy does weird things. Yeah. With no op. So I, I don't do fix that, but now currently multi also depends on lab behavior. Oh, there's the, the 10 of X.

##### **Geohot** [[00:50:58](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3058)]
Got it. Uh, I'm pretty good experience with cloud.

##### **Chenyu** [[00:51:05](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3065)]
It's very useful to understand, uh, the flow and the things in scheduler. It's very useful to read code and like,

##### **Geohot** [[00:51:14](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3074)]
it's, it's amazing at reading. Yeah. Yeah.

##### **Chenyu** [[00:51:18](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3078)]
It's also not bad if I know how to fix this and I just need to type things for me. It also works. It just cannot discover a good solution by itself.

##### **Geohot** [[00:51:31](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3091)]
What I found a lot of these things is you spend time with it reading code. And then once you're confident that you both understand what needs to be done, then it can write it. But if you're not confident after reading what it said, and you just ask it to write it, it gives you totally the wrong thing.

##### **Geohot** [[00:51:44](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3104)]
Yeah.

##### **Nimlgen** [[00:51:47](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3107)]
Yep.

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3111)]
Um, I have found another way to use it too, which is if there's a loop that's very clearly closed and you give it a test that I can't cheat on, then it seems to, if you're willing to burn a lot, a lot of compute, it will eventually figure things out.

##### **Nimlgen** [[00:52:07](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3127)]
Yeah.

##### **Chenyu** [[00:52:07](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3127)]
What I did was for all the range of fire and scheduling rewrite rules, I just asked cloud to write a for loop and try to disable every branch of the code. So I think I can just run a bunch in every rules and see if anything breaks. Yeah. Something like that they can do.

##### **Geohot** [[00:52:22](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3142)]
Yeah. I mean, it's great at like everything you were just too lazy to write the script to do before. It just does for you.

##### **Geohot** [[00:52:29](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3149)]
Yeah.

##### **Geohot** [[00:52:33](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3153)]
But you see the problems with the, you know, that, that GLM flash. It's like, that is, that is still, it was 600 lines. Now it's 150 lines and it's still a hundred lines too many. And if you don't carefully read every line, you just, it just, it's slop. And if you don't, yeah. If you don't stay really on top of that, I think a lot of projects that don't stay on top of this are going to find themselves buried in technical debt. Yeah.

##### **Chenyu** [[00:53:02](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3182)]
I think it's both true that I can say maybe more than 90% of the code I push is written by cloud, but also I delete like 99% of the code that cloud wrote. So I think that's about right.

##### **Geohot** [[00:53:16](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3196)]
Yeah.

##### **Chenyu** [[00:53:19](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3199)]
Yeah. Okay. Yeah. That's, that's my thing. So focusing on like more of this refactor, I think the cat thing might be useful for training and also the, the multi thing. If you find like smaller report, let me know.

##### **Geohot** [[00:53:39](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3219)]
Which multi thing? If I find.

##### **Chenyu** [[00:53:42](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3222)]
I think multi used to have this upside down. But in my optimization, that's multi pass in a smaller dtype. That might be the floor 30 to all reduce thing was cooker, we mentioned earlier. I also believe Multi's some pens to waste for extra coffee for no reason.

##### **Geohot** [[00:54:04](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3244)]
or mixing loads without My stuff. stuff, opened, issues, bounties. The run looks stable with the azim change? Yeah, I'm like 1,000 steps in, and it's stable. So the problem is literally AMD 4. Potentially, yeah. This machine is throttling a bit, though. Oh, you want to turn the fans back up? Oh, is that why? You want me to turn the fans down? Yeah. OK, yeah, I'll turn them back up. We also now have a much smaller set of bounties.

##### **Chenyu** [[00:55:01](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3301)]
Only the ones that's easier to verify and truly useful. Yeah.

##### **Geohot** [[00:55:09](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3309)]
It's not that the other ones weren't useful. It's that, yeah, they weren't worth verifying. These ones that are speed, it's pretty easy to verify. And if someone actually manages to achieve that speed, I'll spend some time saying that this is AI slop, and they need to write it better if they do it with AI.

##### **Geohot** [[00:55:30](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3330)]
Yeah.

##### **Geohot** [[00:55:32](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3332)]
And in general, I don't think we have to get rid of bounties. I think just the bar for bounties goes up. But we did. We had a bounty claimed. Yeah. Yeah. And it's clearly AI code. But I was writing that with AI too. It's fine. The test pass, it's not too much like slop.

##### **Geohot** [[00:55:57](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3357)]
So yeah, we had a bounty claimed yesterday. And we have eight bounties remaining for anybody to try.

##### **Geohot** [[00:56:12](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3372)]
Yeah. Yeah. There's no more. There's no more. Refactor bounties already didn't really work.

##### **Geohot** [[00:56:18](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3378)]
And now they really don't work. Yeah.

##### **Chenyu** [[00:56:26](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3386)]
I think for people who really want to contribute, there's probably like 30 different tiny gray bugs in my head now. So there are tons of stuff to fix.

##### **Geohot** [[00:56:39](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3399)]
Oh, yeah. We should. No one from. From Commas here. But I'll say. I'll say. I'll say file issues. Yeah.

##### **Chenyu** [[00:56:49](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3409)]
Yeah. So I think first is file and issue. And we don't want to block them, but we also need to see how this work graduated works better for them.

##### **Geohot** [[00:57:05](https://www.youtube.com/watch?v=u1TTlOcqeCc&t=3425)]
Oh. File issue first. Yeah. I said a few open issues the repanno. There's a lock. Yeah. Then we will try to figure it out. Anything else? Okay, that's it for this meeting. Thank you everyone. See you next week, same time. Bye bye.
