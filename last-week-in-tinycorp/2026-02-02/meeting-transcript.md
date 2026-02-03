# 2026-02-02 Meeting

### Meeting Agenda

**Time:** new meeting #5, 9am Monday San Diego time
- company update
- jit asserts, assign, mypy
- viz / fast gemm
- drivers
- llama training
- decomp int64
- assembly
- other issues / bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=GL9FmVHIYXs)

### Highlights

- **[USB eGPU board plan](#geohot-000009)**: Received a Common Events box with two USB GPUs; custom firmware is progressing for USB 3/USB 4; plan is to sell the board (an eGPU) for ~$150–$200.
- **[Tinybox + JIT asserts](#geohot-000042)**: FTDI breakout for easy access; Tinybox sales unexpectedly strong; JIT asserts considered finished.
- **[Move Tensor methods into mix-ins/UOPs](#geohot-000157)**: Discussed reducing Tensor surface area by moving methods to UOPs/mix-ins; idea to have Tensor intercept/unwrap UOPs and call UOP functions directly.
- **[Typing status + lambda-heavy rewrites](#chenyu-000359)**: MyPy report suggests ~half the code isn’t fully typed; lots of lambda-based rewrite rules aren’t being type-checked well.
- **[Assign is “super broken”](#chenyu-000556)**: Assign refactor is blocked by incorrect dependency/order tracking and confusing “disk” device semantics (device can’t compute + buffer contiguity assumptions).
- **[Dtype spec + “range of fire” simplification](#geohot-001005)**: Proposed dtype should be “buffer dtype + number of elements” before range-of-fire; after range-of-fire it becomes plain dtype; goal is to unify concepts like index/jit.
- **[Flash-attention kernel priority](#geohot-001157)**: After merging “1.4 payoffs” using Llama, top priority is finding a good flash-attention kernel; plan to email “Jim” about open-sourcing; pursue multiple approaches in parallel.
- **[ASMGEM memory issue at long seq](#geohot-001300)**: ASMGEM hits OOM at larger sequence lengths; suspected extra copies/contiguous conversions; suggested using this as a path to replace custom kernel with `call`.
- **[Replace custom kernel with `call`](#geohot-001412)**: `call` enables removing graph function from custom curves; `define_global` becomes an alias for `param`; kernel/custom-kernel refactor should move UOPs out of args into source0.
- **[AMD fault recovery without reboot](#nimlgen-001915)**: Driver can now handle/print all issues; on non-MI machines can recover from faults without rebooting GPU; AQL reset has an XCC sync issue; current recovery path relies on polling.
- **[Polling delay tuning](#geohot-002045)**: Noted a 2-second polling delay; suggestion to reduce (e.g., ~100ms) and avoid tight-loop polling (sleep-based polling acceptable).
- **[Qualcomm box coherency issue](#nimlgen-002420)**: Investigating CPU/GPU cache/coherency behavior as a likely root cause; marked as priority #1.
- **[NVIDIA trace status](#nimlgen-002458)**: Tracing works with the NVIDIA driver on 4090 and 5090; decoder script parses the format; still investigating odd driver behavior (possibly power/perf-state related).
- **[Apple driver approval mismatch](#geohot-002705)**: Apple validated submitted items, but granted entitlements don’t match; “vendor ID issue” persists; considered low priority.
- **[Llama training shape constraints](#wozeparrot-002755)**: Have a 1496 sequence-length model trained at BS16; expect BS8 @ 8192 to be similar by tokens/step, but 8192 doesn’t fit due to SMGEM constraints.
- **[Flash attention throughput + kernel mix](#geohot-002806)**: Flash attention reported at ~330 TFLOPs; 8192 context is “very small” and workload is dominated by GEMM (~70%).
- **[FFN/output GEMM is wildly slow](#geohot-002906)**: FFN/output GEMM reported ~300ms / ~26 TFLOPs—described as “50x off”; likely a bug or wrong path; plan to benchmark specific GEMM dimensions and verify ASMGEM usage.
- **[Int64 long decomp status](#chrism-003156)**: Long decomp works broadly except where shift support/PTX interactions break; fallback to multiplication is acceptable; denormals aren’t a priority.
- **[PTX/shift ordering constraints](#geohot-003234)**: PTX address rewrite should happen as late as possible; shifting strategy should be “express as multiply, then rewrite to shifts,” not the reverse.
- **[Threefry rules debate](#chenyu-003641)**: Removing threefry rules makes the generated kernel ~10% longer; either improve the general decomp so the hack isn’t needed, or keep rules to preserve kernel quality.
- **[UBSAN idea after AMD -O3 UB](#chrism-003849)**: Hit UB due to signed overflow when AMD compiles with -O3; suggested adding a UBSAN compile mode to catch similar issues (not high priority).
- **[CI stability after cache change](#chrism-004002)**: Since disabling PR cache-saving, no master failures seen due to “connecting to the internet”; could be GitHub Actions improvement or the change helping.
- **[Metal compiler LLVM conflict workaround](#chrism-004039)**: Mac issue traced to metal compiler loading its own LLVM; fix is currently to skip the problematic tests rather than resolve the loader conflict.
- **[Benchmarks should never fail](#geohot-004153)**: Emphasis on getting through compiler work to “image = 1”; added benchmark tests and wants Strix Halo benchmarks; any benchmark failure should lead to CI coverage that would have caught it.
- **[Move tests to NULL device](#geohot-004331)**: Plan to systematically shift tests that don’t need real hardware onto the null device and ensure runners exercise that path.
- **[Assembly emulator via AMD PDF pseudocode](#geohot-004411)**: Swapped to a Python-based emulator with minimal regression; instructions represented as UOPs; pipeline parses AMD PDFs for pseudocode; RDNA4 support merged; RDNA3 backend work planned.
- **[x86 backend direction](#geohot-004635)**: Critique of doing instruction selection post-linearization; prefer instruction selection pre-linearization and register-pressure-aware linearization for better codegen.
- **[USB firmware sprint](#geohot-004829)**: Firmware reflashing workflow is smooth; USB enumeration is close; next is getting PCIe working—goal is fast USB 3 once both USB+PCIe are solid.
- **[Call chains + autodiff + reduce→scan](#geohot-005053)**: Envisions chains of `call` enabling GPU command buffers (and cleaner WebGPU export); also wants `call` to work with derivatives and to replace `reduce` with a more general `scan`.
- **[Llama startup time is too slow](#geohot-005208)**: Llama script spin-up taking ~3 minutes is called out as a major annoyance and sprint goal to fix.
- **[“Zeros” masking bugs](#geohot-005316)**: Some paths return zeros so failures can pass silently; plan is to return NaNs or wrong shapes to surface issues.
- **[GLM flash bounty](#geohot-005340)**: Mentioned a “GLM flash 50 tokens/sec” bounty; hoping it motivates a usable contribution.
- **[Claude/git-history workflow + PR hygiene](#chenyu-005404)**: Using Claude to traverse git history/context is productive; reinforces importance of small, well-written PRs to avoid “CI spiral” fixes.
- **[Docs cleanup](#geohot-005619)**: Intends to add guidance to `humans.md` and possibly delete `cloud.md` as outdated/low quality.


### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=0)]
Welcome everyone to this meeting. So let's start with company update.

##### **Geohot** [[00:00:09](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=9)]
Yeah, I got my box from Common Events. We have two USB GPUs. I think that's the most exciting thing. Progress is being made on our custom firmware for them. We should be able to make it work really well over both USB 3 and USB 4. Our plan is to sell a board. The company is just going to be the board that's in the Common GPU. It's an eGPU for sale for everybody. It'll be like 150, 200 bucks or something.

##### **Geohot** [[00:00:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=42)]
Broken out FTDI so you can access the chat. That's the main thing. Tinybox sales won't quit this week. I don't know why. You gotta get Kimi running on something. I don't want Kimi. Next is my stuff. So I think I finished the JIT asserts.

##### **Chenyu** [[00:01:22](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=82)]
Or maybe I actually finished it last week already, but I don't plan to add more asserts now. I think obviously I'm happy with.

##### **Chenyu** [[00:01:32](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=92)]
For my Pi, we discussed this last week. I fixed all the self-type stuff in mixing.

##### **Chenyu** [[00:01:40](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=100)]
And also the boundary between Tensor and UUP is clean up. There were like some something that was just using the UUP directly instead of like wrapping in a Tensor first, then do the AOU.

##### **Chenyu** [[00:01:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=116)]
So those are all clean up.

##### **Geohot** [[00:01:57](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=117)]
I've been thinking about this. Why do we want mix-ins? Why don't we want Tensor to just recall the method on UUPs?

##### **Geohot** [[00:02:06](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=126)]
Why don't we just move all those methods to UUPs? Oh, because U-Pet also uses those? U-Pet uses a few of them. Yeah, I guess. I mean, I guess you could keep mix-ins for U-Pet.

##### **Geohot** [[00:02:26](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=146)]
That's totally fine too. I'm just saying like move them off of Tensor. Add like a meta call on Tensor that intercepts them and unwraps the UUPs and then calls the UUP function.

##### **Geohot** [[00:02:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=159)]
Oh, that's probably fine. Oh, yeah. I mean, it's not, it's not very different.

##### **Geohot** [[00:02:44](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=164)]
I think we can actually leave the mix-ins too, just for structural purposes. You know, we don't want like one dude to class.

##### **Geohot** [[00:02:48](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=168)]
But yeah, I mean, I'd kind of like to like move everything off of Tensor into mix-ins. I saw you have a comment on the gen stuff. You also want a UUP.gen? Yeah, I mean, I want everything to just like work on UUPs and Tensor as equivalent like.

##### **Chenyu** [[00:03:13](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=193)]
So, what Tensor is just this class that has less kind of mutable because the underlying UUP can be different?

##### **Geohot** [[00:03:21](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=201)]
Exactly.

##### **Chenyu** [[00:03:22](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=202)]
Okay.

##### **Geohot** [[00:03:23](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=203)]
The only difference, yeah, the only thing that I, I mean, UUPs are immutable and Tensor is immutable.

##### **Geohot** [[00:03:28](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=208)]
That's the only difference.

##### **Flata** [[00:03:29](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=209)]
Okay.

##### **Geohot** [[00:03:32](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=212)]
Yeah. So, I guess, I don't know. I mean, I don't know.

##### **Geohot** [[00:03:37](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=217)]
I got like stuck on like moving, like, I moved all the things to mix-ins that didn't need D-type. And then I'm like, I don't know what to do for D-type, but it's not really that hard.

##### **Geohot** [[00:03:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=225)]
I just gotta kind of read down. I don't know if you want to take on moving more things to mix-ins. Nope.

##### **Chenyu** [[00:03:59](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=239)]
Yeah, no, I'm just saying, I think I'm going to be, I'm going to be, I'm going to be I think there are also a bunch of hacks in Tensor. Maybe it's a good, like, motivation to remove those. I would talk about this more in the assign, but I think MyPy, I added like one line stats for the, for the MyPy reports. I think half of our lines are not typed, not like fully typed. And yeah, part of it is the runtime. I don't know if we can do better there because a lot of the runtime types are like auto-gen, which is kind of a good thing. But I think we can ignore. So I don't know how, how improved we can make on that front. Then the other half is the Lambda in general, because we use tons of Lambdas in the rewrite and we have a lot of past to kind of make sure it's that type, but it's not really type checked.

##### **Geohot** [[00:04:51](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=291)]
Well, I mean, if they're Lambdas, can't we type the, the list that we pass into pattern matcher? Have a callable that accepts UOPS and returns a UOPS.

##### **Geohot** [[00:05:06](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=306)]
I can try that, but I don't know how good MyPy is tracking this because you are basically

##### **Chenyu** [[00:05:15](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=315)]
asking MyPy to really wrong the rules to know what the return type is. Right. I don't know if it's smart enough to say, okay, all these rules are list type. So any, any possible compute, compute the output from this. It's also that.

##### **Chenyu** [[00:05:29](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=329)]
I don't think it's less than more.

##### **Geohot** [[00:05:33](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=333)]
No. Well, I'm saying you could at least like, if you make the list type callable that returns with UOPS, at least it could know that the rules return UOPS. It wouldn't help with the input type and it's annoying with context too.

##### **Chenyu** [[00:05:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=345)]
And it's annoying if your output is not UOPS.

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=352)]
Yeah, that kind of shouldn't exist. Yeah.

##### **Chenyu** [[00:05:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=356)]
That's kind of the, unless we have a really big bench on that. I don't think MyPy can do any better. And the rest is probably some like minor thing. Like there are like some of the helpers that obviously returns like bullying. We can have a pass or can have a pass to add all the output types to those. So that's like less important. Then the final thing that I was most excited about was assign. Because assign is super broken. And by, so this started first when I tried to do the make this assign, make this assign lazy. And the thing is, if you ask Cloud to do it, Cloud will happily go hitting the wall and make 10 different changes in different places until the test pass. And when I read it, it doesn't make sense at all. Then you're, and then you will start to realize so many things are hacked around assign and this. So I'm making progress on that. I probably keep working on this for this week, unless I find something I can help with low Lama training. But overall, I find this workflow of using Cloud to go through Git history and to find a context around certain items very useful. I think that shows the. Importance of writing good PR and make it small. But my previous biggest issue working on the scheduler part was I just don't quite understand what certain UOP is supposed to be because it can be very different from the actual implementation. Having like this, you can certainly read Git history and context a lot better than how I would do this, like with the git blame and stuff like that. So you can see my change. I isolated bunch of like arrows and bugs and fix some of it. I think the clear are two major issues for assign. One is the odor is not actually right. So that's, that's the main reason intentionally level. We need to do a lot of realize in places as kind of we manually making sure the dependency is tracked correctly. And then. Which is not right now. Another is like desk. So desk, we used to have a check for desk in the tensor level to say this device is desk. Let's logic is not complete. What we mean by desk is actually a device that cannot do compute. And we kind of always guarantee the underlying buffer is contiguous. So that's the, that's the actual thing we need to. Make our like in different layers. And I think there's a better way to do it because there's not really difference between like a desk memory to your CPU buffer. If it's like a one big memory. If you can do big cast on desk, you should be able to do that on your contiguous memory as well. Things like that. So, yeah, I think there's a huge potential. I think, I think we're in jafi indexing is too long. So I don't know how it will be able to like be cleaner.

##### **Geohot** [[00:09:31](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=571)]
You ready to file should be able to be cleaner. I agree. Yeah.

##### **Chrism** [[00:09:37](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=577)]
Yeah.

##### **Chenyu** [[00:09:38](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=578)]
I also find that with my bunch of rules that is just like no longer needed or because the way we write spec and the way we write allow any length is kind of if you, if you just add it blindly or things were still passed, but it's not necessarily needed. So if I see it, I would just remove it. Something like that.

##### **Geohot** [[00:10:05](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=605)]
Yeah. I've been working on a D type spec. The other thing that I think would help make range of fire a lot shorter is I think tensors have the wrong D type. I think that the D type should actually be D type of back. D type float back and the number of elements. And then after range of fire, it's just D type.

##### **Chenyu** [[00:10:29](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=629)]
What do you mean by number of elements? In the tensor.

##### **Geohot** [[00:10:35](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=635)]
Yeah. The size.

##### **Chrism** [[00:10:38](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=638)]
So also let's just a product of shape.

##### **Geohot** [[00:10:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=642)]
Yes. It's product. It's product. You match shape because it can't be symbolic. Okay. So it's a product. So if you if you look at the range of fire, it's a product.

##### **Geohot** [[00:11:02](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=662)]
And then it's the range of fire. After range of fire runs, it rewrites the UOPS to be like D type float. That's what it is inside of the range.

##### **Geohot** [[00:11:12](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=672)]
And then index and jet become the same thing. Okay. So we currently have jet and R, but it doesn't have to be an R.

##### **Geohot** [[00:11:28](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=688)]
We can put it as a parameter.

##### **Chenyu** [[00:11:31](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=691)]
So we can see this better once we don't have image.

##### **Geohot** [[00:11:34](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=694)]
Yes. Yes. That's a lot of blocker for a lot of this stuff.

##### **Chenyu** [[00:11:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=699)]
Yeah. No, but I see the potential there.

##### **Flata** [[00:11:44](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=704)]
Okay.

##### **Chenyu** [[00:11:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=705)]
Yeah. So I think my next sprint would be to see if there's anything I can help with Lama. Otherwise, I will continue with my happy refactor of the D type. I've got a lot of things that I want to add to my schedule.

##### **Geohot** [[00:11:57](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=717)]
That's me. Next we have a question. As Jim has merged 1.4 payoffs, and it's using Lama. Great. I'm going to find a flash attention kernel next. Are there good flash attention kernels? I don't know. Yeah. I mean, I think we should pursue both strategies in parallel.

##### **Chrism** [[00:12:33](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=753)]
Getting errors to be faster than trying to find one.

##### **Geohot** [[00:12:38](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=758)]
It's a bit more complex than Jim. It is.

##### **Flata** [[00:12:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=765)]
Yeah.

##### **Geohot** [[00:12:46](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=766)]
I'm hoping, I don't know.

##### **Geohot** [[00:12:47](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=767)]
I'm going to email it. I'll email him tomorrow and be like, are you actually seriously going to open source this?

##### **Geohot** [[00:12:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=773)]
Is that going to happen?

##### **Flata** [[00:12:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=775)]
Yeah.

##### **Qazalin** [[00:12:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=776)]
So, I'm going to send it to you. We might be cleaning up the code.

##### **Geohot** [[00:13:00](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=780)]
I hope so. I don't know. Give us a good one. Good. Have a good one. Clean it up. What else you got for this program? So, Asm. Can be used for larger sequence lengths. It goes out of memory.

##### **Flata** [[00:13:23](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=803)]
So, we're going to have to do a little bit of work on that. It's a little bit of a mess.

##### **Geohot** [[00:13:26](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=806)]
What can't be used?

##### **Qazalin** [[00:13:29](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=809)]
Asm. The assembly gem memory issue.

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=814)]
Oh, the assembly gem memory issue. Does that just have to do with the fact that there's contiguouses?

##### **Qazalin** [[00:13:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=819)]
I think so.

##### **Geohot** [[00:13:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=822)]
Yeah. I think we can clean that up. Oh, another thing if you're interested. So, I added call. We should be able to remove the graph function off of custom curves.

##### **Geohot** [[00:14:12](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=852)]
So, that allows me to just remove some of the grid data that was we hadち to replace both kernel, custom kernel, and custom kernel with call.

##### **Qazalin** [[00:14:44](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=884)]
Yeah, I see. I saw you made define global also a param. It's just an alias now.

##### **Geohot** [[00:14:52](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=892)]
Yes, define global is just an alias for param now. We only made one new uup, but I think we can unify. So the problem with kernel right now is it has uups in the arg.

##### **Geohot** [[00:15:05](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=905)]
Those uups should actually just be in source 0. Yeah, uups in args are 0.

##### **Geohot** [[00:15:15](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=915)]
Oh yeah, I don't know if you're interested in that. This project is great. But I think priority one is looking for flash attention kernel. And priority two is refactoring kernel and custom kernel to actually just be call.

##### **Geohot** [[00:15:32](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=932)]
Is there any value in running AMD's benchmark? Oh, AMD's real benchmark? Yeah. I don't know how much of our things that we can . Yeah, we know what they're doing. I mean, we just got to get a breakdown of how actually things are. We need to figure out where our time is going. Oh, sorry. You were saying something?

##### **Qazalin** [[00:16:14](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=974)]
So to be clear, I'm not going to work on the memory stuff. Just the general memory stuff. Oh, okay. Yeah. Yeah.

##### **Geohot** [[00:16:22](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=982)]
I think... I think that memory stuff.. Yeah, the memory stuff is Kn Know. was very related to replacing custom kernel with call.

##### **Qazalin** [[00:16:31](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=991)]
Because then I can't put the assembly in the kernel?

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=997)]
Yeah. You should just be able to...? My theory about what's happening is that it's making extra copies. There's extra contribute existence. And if you look at the code... Custom kernel is kind of a hack. But if you can reduce its南梓 iンStesso foruluntà depths ...

##### **Geohot** [[00:16:51](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1011)]
replace custom kernel with call and only do the contiguous if you need to. I think that'll fix the memory thing, though. See? So it doesn't use contiguous in call.

##### **Geohot** [[00:17:07](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1027)]
Let me see if it does. If it's, like, permuted or something. If the kernel is expecting a different type or drive in the input buffer, then yeah, it needs a contiguous. So I don't

##### **Geohot** [[00:17:23](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1043)]
know what your fast gem is expecting. Maybe it has to do a transpose, or maybe, I don't know. Yeah, I would look into that and use that as a gateway to replacing custom kernel with call. Okay. And for this, I don't really have much work planned since we're left with sqtt. I mean, yeah, it's pretty good. I'm pretty happy with where it is on sqtt. Yeah, I think it's pretty usable. And I think once we start to do RTA3 assembly back end, we can try to see if it's going to work. I gotta focus and rel speed for it. So this worked. This already helped me get from 53 to 55 T trabajar on Amdy gegoutat. Amdy.

##### **Qazalin** [[00:18:25](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1105)]
It was written by .

##### **Geohot** [[00:18:38](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1118)]
Yeah.

##### **Flata** [[00:18:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1122)]
Wow.

##### **Geohot** [[00:18:43](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1123)]
Yeah. Yeah, top priority is Flash Attention Kernels. Second priority is the custom kernel thing. I'll look at the memory thing and at least figure out what it is. Next we have drivers.

##### **Nimlgen** [[00:19:15](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1155)]
So for the AMD we can now handle all issues and we print them. And for Not-MI machines we can also do recovery from these faults without rebooting the GPU. Awesome.

##### **Geohot** [[00:19:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1181)]
Why Not-MI machines?

##### **Nimlgen** [[00:19:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1185)]
I mean, we still have this issue that we need something else to reset for the AQL queue. It works with PM4 but not AQL because they won't sync XCCs after the reset. I mean, they have the same bug in the AMD GPU if I turn off the mass, like the analog of mass.

##### **Geohot** [[00:20:11](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1211)]
So I'm running the external GPU crash now. It's pretty slow. Does it have to do a full reset in between or not?

##### **Nimlgen** [[00:20:20](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1220)]
Oh no, I just start recovery. Basically we have... Yeah, the recovery should be really fast. So basically because we don't use interrupts right now, I mean, we don't have VFIO enabled.

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1237)]
Oh, you're polling for that.

##### **Nimlgen** [[00:20:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1239)]
Yeah. And actually only after two seconds.

##### **Geohot** [[00:20:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1245)]
Why? Two seconds. Why wait two seconds? I can remove that.

##### **Nimlgen** [[00:20:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1256)]
But I mean, for really fast kernel, it's just faster to not poll at all. Just not visit this path.

##### **Geohot** [[00:21:09](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1269)]
But yeah, I can remove that. Yeah, I don't think. I mean, two seconds, sure. Maybe wait 100 milliseconds or something.

##### **Geohot** [[00:21:16](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1276)]
Yeah, okay.

##### **Geohot** [[00:21:17](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1277)]
Yeah. I mean, I would also wouldn't like... Don't poll in a tight loop.

##### **Geohot** [[00:21:21](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1281)]
Just poll in like a sleep or like poll one third millisecond or something. Okay. Cool. Yeah, I think interrupts are not something we need. I'm totally fine with polling. Yeah.

##### **Geohot** [[00:21:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1305)]
Another thing, like my computer gets brought down the whole world quite a bit. If I launch a forever running kernel, will it crash my computer?

##### **Geohot** [[00:21:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1315)]
And is there anything we can do about that? So I don't really get it. So why the kernel should crush your computer?

##### **Geohot** [[00:22:12](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1332)]
If it's like a forever running kernel. It seems like there's some like watchdog timer that if a kernel runs for like three seconds, it brings my whole GPU down. Oh, with AMD GPU?

##### **Nimlgen** [[00:22:24](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1344)]
Yeah.

##### **Chrism** [[00:22:25](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1345)]
So I have a Strix Halo laptop. So I'm running the AMD GPU driver.

##### **Geohot** [[00:22:32](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1352)]
Yeah.

##### **Nimlgen** [[00:22:36](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1356)]
Actually, I'm not aware of that. Basically, I think for sure we will run something longer than three seconds. But yeah, I can just read that kernel. Does this test pass on AMD GPU or only AM?

##### **Geohot** [[00:22:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1373)]
So only AM. Only AM.

##### **Geohot** [[00:22:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1376)]
The external GPU test crash.

##### **Nimlgen** [[00:22:58](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1378)]
Yeah, yeah. Only AM.

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1380)]
Only AM. And I imagine, is there a reason we can't do an AMD GPU or?

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1391)]
Potentially we can.

##### **Nimlgen** [[00:23:14](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1394)]
I know. I'll try that. I mean, the only thing we can do is just try to recreate the, just recreate the queue. And that should work. But I'm not sure actually what will happen with AMD GPU, if it will disconnect our client or not. Yeah, I'll test this. Because actually we need to reset Mac at some point if there are some faults.

##### **Geohot** [[00:23:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1421)]
Got it. But yeah, no, this is cool. It's great. Yeah, I'm running test with your crash right now. It looks good. I wonder if there's... So it all just comes through this, everything is through these SQ interrupts.

##### **Nimlgen** [[00:23:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1435)]
Yeah, yeah. So that's the only place where all hardware sends the interrupts to, including all files.

##### **Flata** [[00:24:03](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1443)]
Right.

##### **Geohot** [[00:24:05](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1445)]
By the way, Divya, I'll use the speaker if you want to talk. You have to exit and leave the meeting. About the... Oh, yeah. This, did you see this box? This Qualcomm box?

##### **Nimlgen** [[00:24:20](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1460)]
Yeah, yeah. I started to take a look into this. There is something about caches. I think it's just the caches and coherency, I think with the CPU and GPU side. So I know I just... Yeah, I'll fix that as soon as I can. Yeah, that's priority number one.

##### **Chrism** [[00:24:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1481)]
Yeah.

##### **Nimlgen** [[00:24:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1481)]
Yeah.

##### **Geohot** [[00:24:45](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1485)]
And then priority number three is the NV trace on the 56. Over NV.

##### **Nimlgen** [[00:24:58](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1498)]
Yeah. So about that in short. So actually everything works with the NVIDIA driver. So both 4090 and 5090. And there is also the decoder script. So that can parse all this format. So yeah, I'm still looking into their driver and just reading it. Actually, I have no idea. But I hope I can always return zeros. So maybe it's something about some power things. I'm not sure really what they do special, but I know. So I'll continue looking into this.

##### **Geohot** [[00:25:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1539)]
My guess would be it's something similar to like the set performance clock on AMD where you put it in like a non-throttling mode.

##### **Geohot** [[00:25:47](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1547)]
Yeah.

##### **Nimlgen** [[00:25:51](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1551)]
Yeah, I'll take a look. I know it's not related actually to the profiling because we have pretty strange behavior to the profiling like requests to the GSP because it never validates them. That's kind of strange. It always returns like success to these requests. Yeah, I'll find that because actually at least NVDA driver works with this. So yeah, but.

##### **Flata** [[00:26:22](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1582)]
Yeah. Yeah.

##### **Geohot** [[00:26:27](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1587)]
And then any update on the Mac?

##### **Nimlgen** [[00:26:32](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1592)]
I received nothing from Apple. So they've verified one of them though, right?

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1599)]
I'm sorry. They validated one of the things, right? Whatever they call it, the approval driver thing.

##### **Nimlgen** [[00:26:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1613)]
I mean, they validated everything I've sent to them. The problem is that we have mismatched with what driver validates and what they granted to us.

##### **Geohot** [[00:27:05](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1625)]
Is this still the vendor ID issue?

##### **Geohot** [[00:27:07](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1627)]
Yeah. Yeah. Yeah. Hopefully they get back to us. I don't know. If it happens, then it happens. I think that'll be great. Yeah. I think that's a good thing to have already once we start selling these boards. Yeah. Lowest priority of all things.

##### **Flata** [[00:27:35](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1655)]
Yeah.

##### **Geohot** [[00:27:38](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1658)]
Anything else? I love seeing these exceptions. They're beautiful. No, that's it. Sounds good. Let's move on to LAMA training.

##### **Chenyu** [[00:27:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1673)]
So, I think that's it.

##### **Wozeparrot** [[00:27:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1675)]
So, we have a 1496 sequence length model trained at BS16. I would expect a BS8 8192 sequence length to train about the same just because the token

##### **Geohot** [[00:28:06](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1686)]
counts per step match. 8192 doesn't fit because of SMGEM. I do wonder if there's value in finding a fused Swigloo kernel. That does like all the... Yeah, it does the full FFN in one kernel and it doesn't... Yeah. How fast do you think you can get our flash attention to it? I'm at 330 TFLOPs right now. Okay. And then do you know what percentage of the TFLOPs that are at 3,000?

##### **Wozeparrot** [[00:28:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1735)]
It's quite small. 8192 is very small context length. I think like 70% is gem.

##### **Geohot** [[00:29:06](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1746)]
Our gems are so fast. So, currently with ASMGEM, the output gem is still quite slow. Really? Yeah. Wrong. Okay. So, what's the FFN? It's like 300 milliseconds. 26 TFLOPs. 26. 26? Yeah.

##### **Qazalin** [[00:29:38](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1778)]
Is it even using ASMGEM?

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1782)]
I think it does get ASMGEM because I see the custom kernel running. Oh, yeah. Let's get the... Get the dimensions of that. We should test that.

##### **Qazalin** [[00:29:54](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1794)]
We should fix it. I tested every single gem and it's way far fast.

##### **Geohot** [[00:30:02](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1802)]
Yeah. Okay. It sounds like there's some bug here or something. Also, I found that AMD3 is slower than AMD4. Is it powered? I don't think so. But like flash attention is 330 on AMD4. I think it's 300 on AMD3. AMD4 also has the...

##### **Qazalin** [[00:30:33](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1833)]
AMD4 has the RM mod. It doesn't have the RM mod in GPU. I don't know if that's different in time mix.

##### **Geohot** [[00:30:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1842)]
Maybe. All my testing is done with AM. That doesn't seem that significant.

##### **Geohot** [[00:30:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1855)]
The 20 TFLOP thing sounds like... 26 TFLOP sounds like a major problem. It sounds like it's 50x off from where things should be. Yeah. If you could benchmark the output of a breakdown, where would you guys go? Yeah. I think the experience is pretty obvious. Yeah. That's close to the AMDs. Okay.

##### **Geohot** [[00:31:20](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1880)]
So, I'm going to test it. Okay. So, we're talking about a short period of time.

##### **Geohot** [[00:31:25](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1885)]
And so, I don't know if you guys are in that situation. If you could measure the time that the CPU is running. So, I'm going to test it.

##### **Chenyu** [[00:31:35](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1895)]
Okay.

##### **Geohot** [[00:31:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1899)]
So, you guys will be in that situation. We'll talk about it later. But we're talking about a short period of time.

##### **Flata** [[00:31:40](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1900)]
It's the same as...

##### **Geohot** [[00:31:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1902)]
Yeah. So, you guys are in that situation, right?

##### **Flata** [[00:31:47](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1907)]
Yeah.

##### **Geohot** [[00:31:48](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1908)]
Yeah. Yeah. uh so next we have the decom

##### **Chrism** [[00:31:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1916)]
yeah um so yeah so i mean in uh the long decomp um is done it's uh i mean it's running on everything except for if there's no shift support or uh ptx um yeah i mean obviously we can just do uh multiplication when we don't have shift support um i don't know yeah the reason i ended up yet is because it's i feel like a lot of the decomp stuff is like already hard enough to read and then like kind of multiplying by you know two to the whatever you're dividing by two to the whatever makes it even harder to read but i can just write a little helper that but you know

##### **Geohot** [[00:32:34](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1954)]
that's that so that's not it's not a blocker i'm a repo blocker do we remove pdx i'm probably moving pdx i'm second it doesn't do anything for us yeah i mean yeah

##### **Chenyu** [[00:32:52](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1972)]
i don't think we use px for anything right and it's also not faster

##### **Geohot** [[00:32:59](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=1979)]
yeah so i would either delete it or if there's some i mean it's only really one thing that causes this problem right i actually think that this might not be worth deleting ptx over because like it's because you're doing decomp to the wrong order if the shift thing is the same problem too right that ptx address rewrite should be the absolute last thing that happens

##### **Chrism** [[00:33:21](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2001)]
yeah i mean the shift thing

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2004)]
we have a lot of things that want to be the last thing that happens and don't interact with others really

##### **Chenyu** [[00:33:37](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2017)]
yeah it's like a regular decomp already want to be the last thing so that it doesn't interact with other symbolic level like changes older things like that

##### **Geohot** [[00:33:46](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2026)]
yeah but no the the the

##### **Flata** [[00:33:49](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2029)]
the

##### **Geohot** [[00:33:50](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2030)]
Enough for your conversation um

##### **Chrism** [[00:33:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2036)]
yeah

##### **Geohot** [[00:33:57](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2037)]
um like the ptx thing for the addresses looks a lot more like instruction selection decom

##### **Geohot** [[00:34:20](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2060)]
But either way,

##### **Geohot** [[00:34:21](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2061)]
I don't care if PTX is skipped. I mean, we're behind on compiler pairs got to get done, and image equals one is going to get done. So let's not get distracted by any of this. Skipping for shift is fine. Skipping for PTX is fine.

##### **Chrism** [[00:34:40](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2080)]
The problem with shift is that we rewrite multiplications to shifts, but no shifts to multiplications. I think there's no decomp that goes the other way around.

##### **Geohot** [[00:34:51](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2091)]
Yeah, there shouldn't be a decomp that goes the other way around. You should do it all as multiplication, and then have it all get rewritten to shift.

##### **Chrism** [[00:34:58](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2098)]
Yeah, yeah, okay, sure. Anyway, that's a later problem to solve.

##### **Geohot** [[00:35:02](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2102)]
Yeah, which backends don't support shift?

##### **Chrism** [[00:35:06](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2106)]
Neuro doesn't support it. I think neuro is the specific one that doesn't support it. If I remember correctly, it's like neuro doesn't support specifically shifting by a variable amount or something like this. I don't know. And it's only certain backends don't support it. Do you ever

##### **Geohot** [[00:35:25](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2125)]
shift by a variable amount? Because that's a different problem. Multiplication can't do that.

##### **Chrism** [[00:35:30](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2130)]
Oh, that's true.

##### **Chrism** [[00:35:32](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2132)]
Yeah, you do. Because you do account leading zeros, and then you shift by that amount.

##### **Geohot** [[00:35:38](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2138)]
For what?

##### **Chrism** [[00:35:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2141)]
Like, for instance,

##### **Chrism** [[00:35:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2142)]
for, well, I guess we're not doing, okay, so for instance, in the float example, you have to do this because you don't do this for long decomp, but in the float example, you have to do this if you want to have decomp. You have to do this for denormals, but I guess if we do denormals or zero, then you don't have to do this.

##### **Geohot** [[00:36:03](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2163)]
Yeah, I don't care about denormals. This is just for decomps. But for N64 decomps, this should work without shift.

##### **Chrism** [[00:36:09](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2169)]
Yeah, no, there's no account leading zeros for that.

##### **Geohot** [[00:36:11](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2171)]
Yeah, okay, great. Yeah, I don't, yeah. Regardless, whatever it is, it's fine. If we can delete the three fry rules, that would be great, but we really got to get to the component, apparently, now.

##### **Chrism** [[00:36:24](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2184)]
Yeah, wait, I saw that message about you tried deleting those, and it was slower. Jenny, what were you saying about like you were saying something about N32, like maybe there's some application for N32? I didn't totally understand what you were saying.

##### **Chenyu** [[00:36:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2201)]
So I don't know if you have tried this, but if you just delete that five rules for three fry,

##### **Chenyu** [[00:36:47](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2207)]
and let the long, like emulate that, you will see the output kernel is like 10% longer. I just guessed it maybe on the AOU counts. So that means those rules are useful in some way, right? Yeah. It's like, it's better, the output kernel is better with those rules than with that. But those rules are also only applied to the N32 and N64. N64? Yeah, N64. Imagine the same rules could be generic to, say, N16 to N32. There's like some relationship that is always true between certain D types, but it's either, so the conclusion here is either our D comp can in general be made better, the way that it's always like fit into 232, maybe there's like missing opportunity, then we should be able to fully mimic this hack. Or, there are something that's just generically true, and we can apply that to smaller ints or like other D types. That was my whole point.

##### **Chrism** [[00:38:00](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2280)]
I see. Okay. Yeah. Yeah, I mean, it should be

##### **Chrism** [[00:38:05](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2285)]
applicable to, smaller D types. I see no reason why it wouldn't be. I think

##### **Chenyu** [[00:38:13](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2293)]
I don't know how important this is, but I would lean more to

##### **Chenyu** [[00:38:19](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2299)]
maybe we just need to improve in 64.

##### **Geohot** [[00:38:24](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2304)]
Okay.

##### **Chenyu** [[00:38:25](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2305)]
But again, it's really not that important. Up to you. I think other things are more important. This is just

##### **Chenyu** [[00:38:34](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2314)]
when we remove the

##### **Chenyu** [[00:38:36](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2316)]
rules, yes, the hack is bad, but also we also want the best version of the generated kernel we can have. So it feels less satisfying to remove rules knowing that the kernel will be worse.

##### **Chrism** [[00:38:49](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2329)]
Yeah, no, I get that. Yeah, that makes sense. Okay, what else? So the other thing with long, that was interesting. So there was that bug with AMD, which is fixed now. But that was a result of the fact that I think the AMD uses 03 when it's compiling. Like under the hood. And so as a result, there was this UB that we were encountering because we were overflowing like a signed integer. And I don't know, I just thought maybe it would be useful to add a flag that allows you to compile with UBSAN and run some tests with that and see if that's run into anything. That feels like it's believable that we run into some sort of bugs. Or fix bugs.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2376)]
Fix some bugs with that. But I don't know. I'm interested to hear thoughts about that. Yeah, I mean, I think it's something that can be done,

##### **Geohot** [[00:39:48](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2388)]
but it's not high priority. The highest priority thing here is getting through the compiler thing and getting to image equals one.

##### **Geohot** [[00:39:54](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2394)]
Yeah.

##### **Chrism** [[00:39:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2395)]
Yep.

##### **Geohot** [[00:39:56](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2396)]
So let's get those things done. And then we can talk about more things.

##### **Chrism** [[00:40:02](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2402)]
Yeah, that's pretty much it. I guess the other thing was CI. Yeah. It seems to be, at least when I went through the scroll back for ever since I made that change that made the PRs not save their caches, we haven't had any failures on master related to connecting to the internet. So either that means that GitHub Actions Internet got really, really good and they fixed it, or they made a difference.

##### **Geohot** [[00:40:29](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2429)]
Cool. Yeah, no, but that seems like a good fix.

##### **Chrism** [[00:40:34](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2434)]
Oh, yeah. It's really good. Is the old plan thing fixed?

##### **Chrism** [[00:40:39](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2439)]
Yes, that is fixed. So that's the same bug as the, it's not fixed, it's just skipped. It's the issue is the same bug as that metal compiler thing where when you load metal compiler, it loads its own LLVM and then because the dynamic micro on Mac OS is not smart enough to reload LLVM, it doesn't, it breaks when you try to open .

##### **Chenyu** [[00:41:04](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2464)]
When I try to fix it. For me locally, cloud also suggests you just load the LLVM into some global or scope so that it will link to the same object.

##### **Chrism** [[00:41:18](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2478)]
I tried a little bit of this. I mean, so one of the problems is that metal compiler loads a different version of LLVM. So that, I don't know how fixable that is.

##### **Chenyu** [[00:41:30](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2490)]
It's also, again, also not probably not very important. It's just slightly annoying. That was a good point. I think that when I run the test locally with auto, something would.

##### **Geohot** [[00:41:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2501)]
Oh no, it's fixed. It just skips them. It just skips them.

##### **Chenyu** [[00:41:43](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2503)]
Yeah, skip is fine. Skip is fine.

##### **Chrism** [[00:41:46](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2506)]
Yeah. This is frustrating and it really feels like there should be some way to solve this. But I don't know.

##### **Geohot** [[00:41:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2513)]
I so much don't care about this. The auto test should always pass for now. And not only should it pass, I added a benchmark test.

##### **Geohot** [[00:42:02](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2522)]
Make sure it keeps passing. There's no benchmark tests on Mac.

##### **Geohot** [[00:42:09](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2529)]
Make sure it keeps passing. And I want to get a benchmark test on Strix Halo. Make sure it keeps passing. And every time that test fails, we have to add something in CI that would have caught

##### **Geohot** [[00:42:18](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2538)]
the failure. But yes, we now have tests in benchmark. But those tests should never fail. It should be fast. Yeah, it's fast. Yeah. Down to zero. Did you do most of that? Like, they've got a lot faster. I know.

##### **Chenyu** [[00:42:42](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2562)]
I just keep skipping things or make things smaller until it runs within a minute on my machine.

##### **Geohot** [[00:42:49](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2569)]
Yeah. Cool.

##### **Chenyu** [[00:42:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2573)]
Yeah, I think we can do better for loads like test separation. I tried some curation for the thing we discussed earlier to move things into units as much as possible and use null as much as possible. We can probably do better. I think a lot of the test ops are like, do we really need like 20 different kinds of get item for every back end? Probably no. Tell me like that.

##### **Geohot** [[00:43:18](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2598)]
No, I think we don't. I think we don't.

##### **Chenyu** [[00:43:20](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2600)]
I think for null, it seems to be fine. Yeah, well, I want to move some tests. Systematically make it a lot faster. I don't think.

##### **Geohot** [[00:43:31](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2611)]
I want to move some tests to null. That's the pass with the null. I mean, so many things like test TQDM that passes with null. Like things that don't even use a device. And then I'll have the unit test runners also run the null test with a null device.

##### **Chenyu** [[00:43:46](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2626)]
Yeah, that sounds fun. Will you do this with whichever, I'm just making sure it's not hard coded device?

##### **Geohot** [[00:43:58](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2638)]
Yeah, I'm doing pretty carefully. Okay, that's good. Cool.

##### **Chenyu** [[00:44:06](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2646)]
Okay, if that's it, next assembly.

##### **Geohot** [[00:44:11](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2651)]
Yeah, some good progress. I mean, last sprint I got, the big thing I did was I switched out Remio. So now the emulator being used is the Python and with almost no speed regression. It's compiling the instructions. The instructions are all in Uops. So it's actually a little bit more complicated. It's actually just there. It's generating tiny grad programs to run instructions. And the key to making it fast was not to compile each instruction, but instead to compile it with the registers being dynamically read. So it uses PC. It has basically a decode stage that reads the registers and then it reads what the register should be and then actually reads from those registers. And then that, yeah, that's it. It's a little bit like beta 10x faster. It's pretty similar in speed to Remio. So that's it. I merged RDNA 4 support today. We'll have emulators for RDNA 3, RDNA 4. CDNA has a lot of weird stuff. The RDNA 4 one still has some bugs too. But it's done in a very nice way where I didn't just tell an LLM to write an emulator. It's parsing all of the P code from AMD's PDFs. It's pulling all of the pseudo code for each instruction out of AMD's PDF. So we have a pretty nice environment for all of AMD's assembly. I still haven't moved it into tiny grad proper. There's still a few rough LLM edges. But if you guys look at the code, hopefully you'll see it's not too terrible. I've aggressively drawn it and equating things up manually. So that's it. I think it's not my highest priority to sprint. My highest priority to sprint is to figure out the D type stuff. Some of the other call stuff that's not the kernel stuff. Basically to try to finally get LLM to be fast.

##### **Geohot** [[00:46:22](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2782)]
The startup time of LLM is way too slow. But basically I'll work on that. Any quick comments on the x86?

##### **Geohot** [[00:46:35](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2795)]
This new one's a lot better. My big complaint about the first one is that it was doing instruction selection after linearization. And at that point you're just rewriting LLVM. But the really interesting thing that we can do in tiny grad is do instruction selection before linearization. And then we can intelligently keep up. And then we can do it in a way that's linearized based on register pressure. So yeah, I think there's something there. I guess maybe this week I'll also start on the RDNA3 assembly backend. LLVM is very good at compiling x86 code. It's terrible at RDNA3. The things that I did with AMD UOP MatMall are totally doable with tiny grad transfer. And that code is almost 2x faster than the AMD UOP MatMall, which uses LLVM. It's very possible to get real speed out of these things because of how GPUs are. They're a lot simpler. They're just very different. The scheduling is very different between CPUs and GPUs. And then if I also... If I also do warp specialization, I think that actually the scheduling... I think everything just becomes a lot easier if you can warp specialize. Because you can independently optimize your GMEM to SMEM and then your SMEM to ALU kernels.

##### **Chrism** [[00:48:19](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2899)]
You can optimize those warps and then one of them is going to be your limiting factor. But you can work on them independently.

##### **Geohot** [[00:48:29](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2909)]
Yeah, so a combination of that stuff. The other thing I want to do this week is work on the USB firmware. So yeah, the box is now set up really nicely so I can reflash the firmware a ton of times. I almost have USB enumerating. And then it'll be a question of getting PCIe to work. And then when PCIe and USB both work, we should be able to finally get fast USB 3.

##### **Geohot** [[00:48:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2933)]
Which is the feature that COM1 wanted for a while.

##### **Geohot** [[00:49:12](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2952)]
And when Photoshop could do this, the promise and resolution would be totally just pretty. So yeah, that's everything in general, but I hope to get all my CPU run out within the next 20 days. But, yeah. I guess I'd like�전 fountain a bowl with you, Daniel. Or maybe check the blog or chat if they've turned on their streams because I think I want to work on that out too. But I just thought it'd be really cool to even chat back with you about that stream talking and the. kernel that crashed my GPU until I added a contiguous. So yeah, that's kind of why I didn't post the music app. It's actually a pretty bad example of pedigree. Because it just concatenates all the nodes together. And it's like I concatenate with like 160 tensors.

##### **Chenyu** [[00:49:51](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2991)]
And that sounds familiar.

##### **Geohot** [[00:49:55](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=2995)]
Yeah, yeah. We're not really designed to concatenate tensors.

##### **Chenyu** [[00:50:01](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3001)]
No, we just need a better synaptic for this and find the optimization and things like that.

##### **Geohot** [[00:50:07](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3007)]
Yeah. Well, the drums it was able to do using tensor operations. But the nodes it did with a big concatenation. I rewrote the drums as basically a, the drums is an expand.

##### **Geohot** [[00:50:25](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3025)]
And every shape. Oh, by the way. I changed your expand outer loop to unroll outer loop. I think that makes more sense. What? What?

##### **Chenyu** [[00:50:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3041)]
When you generate the outer, sorry, outer range. You unroll outer range. That's that was called expand. I was so confused.

##### **Geohot** [[00:50:53](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3053)]
Oh, yeah. I mean, the outer range stuff is super broken. We have to basically get call to work. So there's two aspects of call. There's the call replaces kernel and custom kernel. And then eventually we're going to be left with chains of calls. And these chains of calls can use tiny graph rewrite rules to create GPU command buffers. This also gets to like the, have the correct way to web GPU export and stuff. But here's the other side of call, which is another thing I want to work on this sprint. To get call to work with derivatives. And to get like basically to replace reduce with scan. Because we have reduced right now and reduce has this UOP add. But you should be able to do a reduce with any arbitrary function.

##### **Geohot** [[00:51:46](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3106)]
So yeah, replace reduce with a scan. Yeah. Yeah.

##### **Geohot** [[00:51:57](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3117)]
But the main thing that I want done at the end of this sprint is a faster Lama. How am I going to go about that? It shouldn't take so long to run. I mean, the Python time.

##### **Geohot** [[00:52:08](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3128)]
Like it shouldn't take three minutes to spin up the Lama script. It's annoying. Sounds good.

##### **Chenyu** [[00:52:20](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3140)]
Okay. What are your issues, Monty? I see Flotta here. Are you trying anything with Flotta? Does it work?

##### **Flata** [[00:52:30](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3150)]
I got the eval working. I'm running it right now. Just want to make sure I got the correct loss on that. Because I'm using the weights from the from Hugging Face. So I'm on that. But I think the training loop should be pretty similar as well. So yeah, still progressing through.

##### **Geohot** [[00:52:50](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3170)]
Okay. Oh, why isn't it working?

##### **Flata** [[00:53:00](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3180)]
Your

##### **Geohot** [[00:53:01](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3181)]
issues.

##### **Geohot** [[00:53:16](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3196)]
not give you zeros. Everything's pass on the No backpack and because zeros happen to pass in. Everything has zeros. Okay.

##### **Geohot** [[00:53:25](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3205)]
Yes, that's the annoying part. Yeah, I'll fix that. I'll have it return Nans or something. I'll just be the wrong shape.

##### **Geohot** [[00:53:40](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3220)]
Oh, I have the GLM flash, 50 tokens per second bounty.

##### **Geohot** [[00:53:46](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3226)]
That's pretty motivated. We'll see if he comes through with anything. I think the... I don't know. We'll see if we can get good things out of this. I think for...

##### **Chenyu** [[00:54:04](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3244)]
This is to the bug you posted earlier and the two PRs immediately after. It's like, if you ask Cloud to do it, it would give you that two solutions. I know. Then you can try to... I think for other people who want to try this workflow, a lot of it really is you really need to understand why certain things

##### **Geohot** [[00:54:35](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3275)]
work a certain way and what spec is good or not.

##### **Chenyu** [[00:54:47](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3287)]
If I don't see a clean solution, I will merge mine. Oh, you have a clean solution for that? Well, I just merge after the reduce2x if it's referencing to the same rank.

##### **Geohot** [[00:55:02](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3302)]
Yeah.

##### **Chenyu** [[00:55:03](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3303)]
But not as a separate rewrite step and check that with the rewrite context. So the problem for that two PRs is they try then CI fast, they ask Cloud to fix it, then it goes into a spiral of fixing random stuff.

##### **Chrism** [[00:55:24](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3324)]
I think that just wouldn't work.

##### **Geohot** [[00:55:27](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3327)]
It shouldn't be a lot of lines. It's one straightforward problem.

##### **Geohot** [[00:55:31](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3331)]
Yeah.

##### **Chenyu** [[00:55:34](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3334)]
Even there are more refactors down there. It's just very hard for an external contributor to first refactor those stuff.

##### **Geohot** [[00:55:46](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3346)]
You have to spend some time understanding it. You have to go into the

##### **Chenyu** [[00:55:49](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3349)]
There are a lot more that can be explored and understood before proposing a solution.

##### **Geohot** [[00:56:19](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3379)]
Even asking Cloud to do this helps the output. I'll add it to humans.md. They should all read it before.

##### **Chenyu** [[00:56:32](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3392)]
Oh, and we probably want to

##### **Chenyu** [[00:56:36](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3396)]
either maintain the Cloud.md or or don't have lag.

##### **Geohot** [[00:56:41](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3401)]
I kind of feel like we can delete it. It's kind of crappy. We can just delete it. Okay. Cool.

##### **Chenyu** [[00:56:50](https://www.youtube.com/watch?v=GL9FmVHIYXs&t=3410)]
Sounds good. I think that's it for this meeting. Thank you, everyone. See you next week. Bye-bye.
