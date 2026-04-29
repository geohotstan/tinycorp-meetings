# 2026-04-29 Meeting

### Meeting Agenda

**Time:** new meeting #17, 4/28 9am Tuesday San Diego time
- company update
- MLPerf LLaMA
- new DEV
- vecless
- tensor UOp mixin
- JIT refactor
- viz
- bounties, issues, Comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=z0SgQk_yySo)

### Highlights

- **[Company Update](#geohot-000021)**: New GPU dock prototypes arrived; testing, USB4 validation, firmware checks, load tests, and stress tests are planned before launch, with a goal of 1,000 units in stock.
- **[Tentative Launch Date](#geohot-000049)**: The GPU dock launch is tentatively targeted for May 21, though Geohot cautioned that the date may slip.
- **[MLPerf LLaMA Run](#wozeparrot-000144)**: The team achieved its first sub-three-hour LLaMA run, with a reported time of about 2 hours 57 minutes.
- **[MLPerf Submission Readiness](#chenyu-000241)**: The run still needs proper MLPerf logging, required fields, and compliant evaluation frequency before it can be trusted for submission.
- **[LLaMA Performance Gaps](#nimlgen-000339)**: Remaining slowdown is attributed to slower GEMM, slower flash attention, and extra copies from function behavior; realistic near-term time was estimated around 2:45.
- **[New DEV Improvements](#chrism-000653)**: The new device interface now supports AMX, BSD AMD64 fixes, multiple USB devices, USB 3.0 on Mac, and richer `python -m tinygrad.device` output.
- **[Device Listing Scope](#chenyu-001345)**: Anything capable of running kernels correctly should appear in `tinygrad.device`, including materially different backend/device combinations.
- **[Vecless Progress](#geohot-001426)**: The vecless rewrite shifted from a broad devectorizer/expander rewrite to replacing `vcount` logic with shape-based logic, though load fusion and load shape syntax remain unresolved.
- **[Tensor UOp Mixin Refactor](#chenyu-001801)**: Tensor has been reduced to roughly 800–900 lines, with blockers including multi, training-dependent methods, input-dependent ops, concat/bitcast behavior, disk paths, random APIs, and getitem semantics.
- **[Tensor Forwarder Direction](#geohot-002702)**: The desired end state is for Tensor to stop subclassing `OpMixin` and instead use a forwarder that creates functions, with pure function/call separation.
- **[JIT and ExecItem Refactor](#nimlgen-003245)**: ExecItem was removed, JIT and schedule now use `run_linear`, runners are being removed, and CompiledRunner is next on the chopping block.
- **[UOp Runtime Graph Vision](#geohot-003510)**: Longer term, AMD ComputeQueue and CopyQueue should become UOp graph renderers that emit device-specific command bytes, analogous to rendering WebGPU graphs into JavaScript.
- **[Viz and Profiling Work](#qazalin-004434)**: The team reproduced Kimi’s result on M3, cleaned up CLI defaults, and is moving toward bigger models while investigating RDNA4 WMA/VALU overlap behavior.
- **[MLPerf Optimization Sprint](#geohot-004836)**: Profiling, LLM-assisted search, and human tuning are being directed toward making MLPerf faster, with 2:45 good, 2:30 better, and 2:15 considered highly competitive.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=0)]
Great. I will update the event time after the meeting. So for people here now next week, we will be back to Monday this time.

##### **Chenyu** [[00:00:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=13)]
Okay, let's get started. I'll start with the update.

##### **Geohot** [[00:00:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=21)]
Not too much to say here. We got some new prototypes, the new GPU docks in. Back in the office, do a lot of testing on those, get those ready for launch. We'll try to have a thousand in stock on launch day. We think that this might be one of the highest sales days in history.

##### **Chenyu** [[00:00:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=45)]
Do we have a launch date?

##### **Geohot** [[00:00:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=49)]
Tentatively May 21st, but it's not going to be hit.

##### **Nimlgen** [[00:01:11](https://www.youtube.com/watch?v=z0SgQk_yySo&t=71)]
May 21st.

##### **Chenyu** [[00:01:12](https://www.youtube.com/watch?v=z0SgQk_yySo&t=72)]
Oh, great. I will be there.

##### **Nimlgen** [[00:01:14](https://www.youtube.com/watch?v=z0SgQk_yySo&t=74)]
Cool.

##### **Geohot** [[00:01:16](https://www.youtube.com/watch?v=z0SgQk_yySo&t=76)]
Yeah, we'll definitely have them. I just want to test them, do the USB4 stuff.

##### **Geohot** [[00:01:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=82)]
Make sure our firmware works with this before. We'll do all the load tests, stress tests.

##### **Nimlgen** [[00:01:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=90)]
Yeah.

##### **Wozeparrot** [[00:01:33](https://www.youtube.com/watch?v=z0SgQk_yySo&t=93)]
Sounds good. Anything else?

##### **Nimlgen** [[00:01:36](https://www.youtube.com/watch?v=z0SgQk_yySo&t=96)]
Nope.

##### **Chenyu** [[00:01:38](https://www.youtube.com/watch?v=z0SgQk_yySo&t=98)]
Okay. Let's move on. We start with LLaMA?

##### **Wozeparrot** [[00:01:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=104)]
We had our first under three hour run.

##### **Nimlgen** [[00:01:47](https://www.youtube.com/watch?v=z0SgQk_yySo&t=107)]
Great.

##### **Chenyu** [[00:01:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=108)]
Where is our under three hour run?

##### **Wozeparrot** [[00:01:51](https://www.youtube.com/watch?v=z0SgQk_yySo&t=111)]
Let me look for it.

##### **Nimlgen** [[00:01:54](https://www.youtube.com/watch?v=z0SgQk_yySo&t=114)]
Okay. Okay.

##### **Wozeparrot** [[00:02:04](https://www.youtube.com/watch?v=z0SgQk_yySo&t=124)]
That runs under three hours. This is...

##### **Geohot** [[00:02:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=145)]
It says two hours, 57 minutes. Okay. Okay. Okay. Are we sure it's...

##### **Chenyu** [[00:02:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=152)]
So this doesn't include logging, right?

##### **Geohot** [[00:02:36](https://www.youtube.com/watch?v=z0SgQk_yySo&t=156)]
This doesn't include... Yeah. No MLPerf logging.

##### **Chenyu** [[00:02:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=161)]
Okay. But to your best knowledge, this with logging should be good for submission? Yes. I trust you on all the frequency of eval and things like that. Wait. Why does it not have logging?

##### **Wozeparrot** [[00:02:57](https://www.youtube.com/watch?v=z0SgQk_yySo&t=177)]
It doesn't have MLPerf logging.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=z0SgQk_yySo&t=179)]
Why not?

##### **Wozeparrot** [[00:03:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=180)]
We only do that when you do run_and_time.

##### **Geohot** [[00:03:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=183)]
Oh. And we should be doing that. We should always be doing that. Does it add time? No.

##### **Nimlgen** [[00:03:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=189)]
Yeah.

##### **Chenyu** [[00:03:11](https://www.youtube.com/watch?v=z0SgQk_yySo&t=191)]
Yeah. I think just make sure logging is there and all the required fields are logged and the eval frequency or whatnot, that's to the rules. Then that would be good.

##### **Nimlgen** [[00:03:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=203)]
Yeah.

##### **Wozeparrot** [[00:03:26](https://www.youtube.com/watch?v=z0SgQk_yySo&t=206)]
What's the main difference?

##### **Geohot** [[00:03:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=210)]
It's a lot of stuff.

##### **Wozeparrot** [[00:03:33](https://www.youtube.com/watch?v=z0SgQk_yySo&t=213)]
It's just a lot more custom kernels.

##### **Geohot** [[00:03:38](https://www.youtube.com/watch?v=z0SgQk_yySo&t=218)]
Why are we still 50% slower than...

##### **Nimlgen** [[00:03:39](https://www.youtube.com/watch?v=z0SgQk_yySo&t=219)]
Our GEMM is slower. Our flash attention is slower.

##### **Wozeparrot** [[00:03:39](https://www.youtube.com/watch?v=z0SgQk_yySo&t=219)]
It's a bit slower, and then function makes a copy.

##### **Geohot** [[00:04:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=247)]
Yeah, I mean, this is a lot of that. We fix that. Function makes a copy and it saves.

##### **Wozeparrot** [[00:04:17](https://www.youtube.com/watch?v=z0SgQk_yySo&t=257)]
What's the one-liner to the benchmark? It should take two minutes, right? Do you know how many runs do we need for this?

##### **Geohot** [[00:04:36](https://www.youtube.com/watch?v=z0SgQk_yySo&t=276)]
Five. Okay, so we're going to do this in this day.

##### **Wozeparrot** [[00:04:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=284)]
Nice.

##### **Chenyu** [[00:04:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=288)]
And this MFU is compared to what?

##### **Chenyu** [[00:04:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=293)]
I see 18 something percent, but is this like a super fast? Something.

##### **Wozeparrot** [[00:04:58](https://www.youtube.com/watch?v=z0SgQk_yySo&t=298)]
The MFU is not entirely accurate. It's a pretty bad metric because we don't have everything as FP8. The alpha head is not FP8. The flash attention is not FP8.

##### **Geohot** [[00:05:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=313)]
But that 18% is of the FP8.

##### **Wozeparrot** [[00:05:16](https://www.youtube.com/watch?v=z0SgQk_yySo&t=316)]
Yes.

##### **Geohot** [[00:05:18](https://www.youtube.com/watch?v=z0SgQk_yySo&t=318)]
That's a decent metric stuff. It's theoretically what you can get if you

##### **Geohot** [[00:05:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=322)]
saturated the... Okay. So realistically, our time is probably going to be like two hours 45. Yeah.

##### **Wozeparrot** [[00:05:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=334)]
Okay.

##### **Chenyu** [[00:05:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=337)]
Yeah, it's about two or three weeks.

##### **Chenyu** [[00:05:39](https://www.youtube.com/watch?v=z0SgQk_yySo&t=339)]
So I think it's important to make sure the logging is correct. These things we can fix as early as possible.

##### **Wozeparrot** [[00:05:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=348)]
I'm doing that. I mean, this sprint is basically submission sprint, I think.

##### **Geohot** [[00:05:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=353)]
What's the deadline?

##### **Wozeparrot** [[00:05:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=355)]
Submission is May...

##### **Chenyu** [[00:05:57](https://www.youtube.com/watch?v=z0SgQk_yySo&t=357)]
I think 17th. I suppose it...

##### **Wozeparrot** [[00:05:59](https://www.youtube.com/watch?v=z0SgQk_yySo&t=359)]
I hope you're...

##### **Geohot** [[00:06:01](https://www.youtube.com/watch?v=z0SgQk_yySo&t=361)]
Very cool.

##### **Chenyu** [[00:06:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=367)]
Yeah, it's May 11th. Yeah, about like two weeks.

##### **Geohot** [[00:06:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=373)]
Oh, it's May 11th. It's not 17th.

##### **Wozeparrot** [[00:06:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=381)]
Wait, is it 11th?

##### **Nimlgen** [[00:06:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=390)]
Yeah.

##### **Wozeparrot** [[00:06:31](https://www.youtube.com/watch?v=z0SgQk_yySo&t=391)]
Oh, I'm confused. Okay, I will double check. It's that week.

##### **Geohot** [[00:06:39](https://www.youtube.com/watch?v=z0SgQk_yySo&t=399)]
Okay, anything else for LLaMA?

##### **Wozeparrot** [[00:06:42](https://www.youtube.com/watch?v=z0SgQk_yySo&t=402)]
That's about it.

##### **Geohot** [[00:06:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=406)]
Okay.

##### **Chenyu** [[00:06:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=408)]
Let's move on. The next is the new DEV. What's new?

##### **Chrism** [[00:06:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=413)]
Yeah. Let's do it. Yeah, I mean, the syntax hasn't really changed all that much. I think it's pretty... Yeah, I mean, the syntax hasn't really changed all that much.

##### **Nimlgen** [[00:06:58](https://www.youtube.com/watch?v=z0SgQk_yySo&t=418)]
Yeah. Yeah.

##### **Chrism** [[00:06:58](https://www.youtube.com/watch?v=z0SgQk_yySo&t=418)]
It's stable now. But, yeah, so now you can put AMX in there. And I don't actually have a Windows on ARM laptop to test, but it should work now. And also, apparently, we didn't support BSD AMD64. We just put lowercase amd64. So that should be fixed now, too. But, yeah, if there's any other machines that people run into and they're like, oh, this doesn't work, then open an issue or send a message. There's also a new... When you run `python -m tinygrad.device`, it'll print more... It'll print the interfaces.

##### **Geohot** [[00:07:36](https://www.youtube.com/watch?v=z0SgQk_yySo&t=456)]
So, like, you know, if an interface doesn't come up, then it should tell you why. And then it shows you which ones are available. And also...

##### **Wozeparrot** [[00:07:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=475)]
Like, how many devices you have available on each one.

##### **Geohot** [[00:08:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=480)]
Still complaining about that runtime warning.

##### **Wozeparrot** [[00:08:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=483)]
Yeah. Basically, you need to make all the imports in `tinygrad/__init__` lazy.

##### **Geohot** [[00:08:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=493)]
Wait, you should only have to make the `tinygrad.device` import, like, make all of them lazy. That's annoying. Oh. Because they probably import `tinygrad.device`.

##### **Chrism** [[00:08:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=505)]
Okay, yeah. That makes sense. It's something... It's not a real error, because this, like, module doesn't actually...

##### **Geohot** [[00:08:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=514)]
I'm not that worried about that.

##### **Chrism** [[00:08:35](https://www.youtube.com/watch?v=z0SgQk_yySo&t=515)]
It is annoying.

##### **Wozeparrot** [[00:08:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=517)]
Yeah.

##### **Geohot** [[00:08:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=517)]
The more annoying is that NV calls sudo. It's really annoying.

##### **Wozeparrot** [[00:08:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=524)]
Hmm. What? If it's not passwordless sudo, it hangs or something?

##### **Chrism** [[00:08:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=533)]
I don't know why it calls sudo. But there are a few, like, for sudo within the codebase, there are a couple instances of sudo, whatever.

##### **Geohot** [[00:09:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=540)]
Those are good things to clean out. Yeah.

##### **Geohot** [[00:09:04](https://www.youtube.com/watch?v=z0SgQk_yySo&t=544)]
Um...

##### **Wozeparrot** [[00:09:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=545)]
It also reserves huge pages before it initializes NV.

##### **Chrism** [[00:09:10](https://www.youtube.com/watch?v=z0SgQk_yySo&t=550)]
Oh, does it? Yeah. Because I think I've seen this on Comma devices before, where it complains that this file doesn't exist. Yeah. Yeah, it sounds like that sort of stuff can be cleaned up. Um...

##### **Nimlgen** [[00:09:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=563)]
Yeah. Yeah.

##### **Chrism** [[00:09:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=563)]
I don't know. Oh, yeah. You can have multiple USB devices plugged into your laptop now, and that works. I tested it with the openness multi-GPU, and it worked. USB 3.0 works on Mac now also. Previously, it would work the first time you ran something, but then it wouldn't work the second time. But now it works as many times as I've run it, so...

##### **Geohot** [[00:09:50](https://www.youtube.com/watch?v=z0SgQk_yySo&t=590)]
Cool. Is this the same interface stuff?

##### **Chrism** [[00:09:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=592)]
Yeah. It looks like... I don't know if it's actually a bug in IOKit, but it's something about IOKit behaving differently than what Linux does when you...

##### **Geohot** [[00:10:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=603)]
Yeah, it's probably correct. You should have the endpoints on the same interface anyway, the stock firmware does.

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=z0SgQk_yySo&t=611)]
Uh, which one was it? The same... You can only use it once issue?

##### **Chrism** [[00:10:19](https://www.youtube.com/watch?v=z0SgQk_yySo&t=619)]
Oh, yeah. They experienced the same bug, and it, like, it's not a bug. The symptoms were very similar, but the solution was very different.

##### **Geohot** [[00:10:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=630)]
But I think that's mostly it.

##### **Chenyu** [[00:10:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=632)]
Like, there's other... So, should `tinygrad.device` show mock?

##### **Chrism** [[00:10:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=637)]
No. I intentionally excluded that. I could include it, but I thought it was just kind of confusing, because, like, most people probably don't want to run on mock.

##### **Geohot** [[00:10:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=645)]
Oh, I think we should definitely include mock. Okay.

##### **Chrism** [[00:10:47](https://www.youtube.com/watch?v=z0SgQk_yySo&t=647)]
All right.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=648)]
Yeah, I mean, it's kind of interesting, because, like, then you get, like, AMD, right? Like, AMD... Yeah. Yeah, I think we should include it. I don't think there's a reason to exclude it. It's wrong. It's not like null. I don't think we should include null, but mock is correct. You can almost use it.

##### **Chrism** [[00:11:12](https://www.youtube.com/watch?v=z0SgQk_yySo&t=672)]
The other thing I considered putting in there was, like, you could put, like, the architecture of the devices that are available. So, if you're like, oh, well, you know, what do I have plugged in over USB? Oh, you have GFX 1200 plugged in over USB.

##### **Nimlgen** [[00:11:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=683)]
Yeah.

##### **Geohot** [[00:11:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=683)]
Yeah. We could also print the total RAM.

##### **Chrism** [[00:11:27](https://www.youtube.com/watch?v=z0SgQk_yySo&t=687)]
Oh, yeah.

##### **Geohot** [[00:11:29](https://www.youtube.com/watch?v=z0SgQk_yySo&t=689)]
Yeah. How much RAM each device has. If we have, like, generic tools to... Yeah. ...to query that. Will it show me the number of devices I have?

##### **Chrism** [[00:11:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=697)]
Yeah, it's right there. Right below KFD. Cool.

##### **Wozeparrot** [[00:11:47](https://www.youtube.com/watch?v=z0SgQk_yySo&t=707)]
I'm so used to just it's just stitching a tiny box down, but that's not fast anymore.

##### **Nimlgen** [[00:11:51](https://www.youtube.com/watch?v=z0SgQk_yySo&t=711)]
Yeah. I don't know.

##### **Geohot** [[00:11:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=716)]
I'm just going to go ahead and do that. But if there's anything else that would be useful to put in there, also maybe JSON is

##### **Chrism** [[00:12:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=720)]
useful if... I don't know if we see the LLMs find this useful to look at. Like, the way that I feel like I use the LLMs, I usually tell them what device I want to run on so that they don't really need to query the devices that are available, but maybe

##### **Geohot** [[00:12:14](https://www.youtube.com/watch?v=z0SgQk_yySo&t=734)]
it's useful. Like booting the GPUs? Why is it so slow? Yeah.

##### **Wozeparrot** [[00:12:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=743)]
Uh...

##### **Nimlgen** [[00:12:27](https://www.youtube.com/watch?v=z0SgQk_yySo&t=747)]
I don't know.

##### **Wozeparrot** [[00:12:28](https://www.youtube.com/watch?v=z0SgQk_yySo&t=748)]
It's not that slow on my computer. I should try. Is the client fast? It's slow on my computer, but it can hang here. What happened?

##### **Geohot** [[00:12:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=765)]
AMD hang.

##### **Wozeparrot** [[00:12:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=766)]
AMD hang?

##### **Geohot** [[00:12:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=769)]
Yes.

##### **Wozeparrot** [[00:12:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=772)]
No, it's like in, like... Who knows what kind of state? On the Mac.

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=782)]
What fails on the Mac so we can fix that?

##### **Wozeparrot** [[00:13:04](https://www.youtube.com/watch?v=z0SgQk_yySo&t=784)]
Oh. Well, the AMD driver wasn't started.

##### **Geohot** [[00:13:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=788)]
The kernel. All right. So much for that computer.

##### **Nimlgen** [[00:13:17](https://www.youtube.com/watch?v=z0SgQk_yySo&t=797)]
Okay.

##### **Geohot** [[00:13:19](https://www.youtube.com/watch?v=z0SgQk_yySo&t=799)]
Oh.

##### **Chrism** [[00:13:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=801)]
Yeah. If there's anything else that's useful to you, just let me know. That would be useful to be printed there, or that you think maybe an LLM would like to have access to, or whatever. You can definitely put it there.

##### **Wozeparrot** [[00:13:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=812)]
And yeah. Whatever seems...

##### **Nimlgen** [[00:13:39](https://www.youtube.com/watch?v=z0SgQk_yySo&t=819)]
Cool.

##### **Wozeparrot** [[00:13:43](https://www.youtube.com/watch?v=z0SgQk_yySo&t=823)]
Okay. Looks good.

##### **Chenyu** [[00:13:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=825)]
I think anything that can read... Anything that can run kernels and run them correctly, we want to show here.

##### **Chrism** [[00:13:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=832)]
Yeah. I'm sorry.

##### **Nimlgen** [[00:13:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=832)]
I'm sorry. I'm sorry. I'm sorry. I'm sorry. Yeah.

##### **Chrism** [[00:13:54](https://www.youtube.com/watch?v=z0SgQk_yySo&t=834)]
I mean, do you want to show mock KFD?

##### **Geohot** [[00:13:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=836)]
Is that the same thing? You can decide. It's like... Yeah.

##### **Chenyu** [[00:14:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=843)]
Basically, all these combinations that is materially different, we can use it to run actual kernels, which is listed here.

##### **Nimlgen** [[00:14:12](https://www.youtube.com/watch?v=z0SgQk_yySo&t=852)]
Okay. Yeah.

##### **Geohot** [[00:14:14](https://www.youtube.com/watch?v=z0SgQk_yySo&t=854)]
Makes sense.

##### **Nimlgen** [[00:14:17](https://www.youtube.com/watch?v=z0SgQk_yySo&t=857)]
Okay.

##### **Wozeparrot** [[00:14:18](https://www.youtube.com/watch?v=z0SgQk_yySo&t=858)]
Next. I just put vecless.

##### **Chenyu** [[00:14:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=863)]
Okay.

##### **Nimlgen** [[00:14:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=863)]
Yeah.

##### **Geohot** [[00:14:26](https://www.youtube.com/watch?v=z0SgQk_yySo&t=866)]
So, my first approach was too ambitious. My first approach was like a rewrite of the devectorizer and the expander. It's doable, but I don't think that's probably the right way to do it. My second thing, which is working, is mostly working, is I just replaced the... I just fixed all the logic. Everywhere you used to look for vcount, it just looks for shape. And yeah, this mostly works. I have to still solve the problem of how to specify... So, I have it working. It's correct, but it's not doing load fusion. I have to figure out how we want to specify, right? Because right now, the way that we specify a load for is through the dtype.vec. That's the only one that is like this. It's just loads. So, yeah. I have to figure out how to...

##### **Wozeparrot** [[00:15:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=923)]
I have to figure out what the new syntax for that to be. Yeah. It was slow going last week.

##### **Chenyu** [[00:15:35](https://www.youtube.com/watch?v=z0SgQk_yySo&t=935)]
You can just load a new one, stack.

##### **Geohot** [[00:15:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=941)]
So, stack is just a replacement for devectorize, right? Stack is just... Stack is just a movement on... Sorry. Stack is a replacement for vectorize. So, stack is just like stack the tensors. Yeah.

##### **Wozeparrot** [[00:15:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=953)]
Or you just...

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=955)]
Create a leading axis and stack the tensors.

##### **Wozeparrot** [[00:15:57](https://www.youtube.com/watch?v=z0SgQk_yySo&t=957)]
Yeah, yeah.

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=z0SgQk_yySo&t=958)]
But this doesn't answer... This still doesn't solve the problem of load, right? Like, the problem with load is how many elements do I want to load? That's not really specified anywhere.

##### **Geohot** [[00:16:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=969)]
You can load a shape. Yeah, you can load a shape, right? That's...

##### **Geohot** [[00:16:17](https://www.youtube.com/watch?v=z0SgQk_yySo&t=977)]
Yeah. I just don't know what I want to do for that. Yeah, that makes sense. Well, I mean, loading a shape gets really interesting because then, like, you want to load a 2D shape? Where's the stride?

##### **Geohot** [[00:16:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=990)]
No, no, no, no. I guess... I can't think of a shape.

##### **Geohot** [[00:16:36](https://www.youtube.com/watch?v=z0SgQk_yySo&t=996)]
Yeah, I mean, there's some things that kind of, like, do...

##### **Chenyu** [[00:16:40](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1000)]
Do you have instructions for those weird stuff?

##### **Geohot** [[00:16:43](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1003)]
Yeah, right?

##### **Chenyu** [[00:16:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1005)]
Some of those DSP stuff can load weird patterns.

##### **Geohot** [[00:16:50](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1010)]
Not that weird. It's just... The DSP is pretty straightforward, but the thing that the DSP can do interesting patterns on is the L2 cache prefetch instruction.

##### **Geohot** [[00:17:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1020)]
That can do 2D patterns.

##### **Wozeparrot** [[00:17:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1025)]
Okay.

##### **Geohot** [[00:17:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1027)]
Yeah, I mean, I think eventually we want to move load to copy anyway. I don't know. I had a lot of wrap-up stuff to work on last week.

##### **Geohot** [[00:17:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1043)]
I didn't get a lot of time on it. Okay. But...

##### **Chenyu** [[00:17:28](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1048)]
Okay. Yeah.

##### **Chenyu** [[00:17:28](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1048)]
I'm really looking forward to vecless being done because some of the mixin stuff is blocked by that.

##### **Geohot** [[00:17:35](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1055)]
Okay. Yeah, yeah, yeah. That, and USB4.

##### **Wozeparrot** [[00:17:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1061)]
We'll do this. Anything else? Oh, I think we're good.

##### **Nimlgen** [[00:17:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1072)]
Yeah. Yeah. Okay.

##### **Geohot** [[00:17:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1075)]
Next is all mixin stuff.

##### **Chenyu** [[00:18:01](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1081)]
So made good progress. I think now tensor is like 800 lines, 800, 900 lines, but down another 200.

##### **Chenyu** [[00:18:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1093)]
Anything that's left is either intentional. So two things I think that's blocking cleaning this further. One is multi. I don't know if we want to rethink multi or do something about it. Multi now is slightly annoying.

##### **Geohot** [[00:18:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1114)]
Yeah, I mean, multi is clearly wrong.

##### **Geohot** [[00:18:38](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1118)]
The vec stuff I know the solution for; the multi stuff I don't know the solution for yet.

##### **Chenyu** [[00:18:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1125)]
Yeah, multi is annoying. And some of the methods has different behavior for training. And those, I also don't see how to move. So for example, like attention or dropout or anything that touches that. Then there's anything that's input dependent, like nonzero or mask_select that calls to item now.

##### **Chenyu** [[00:19:15](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1155)]
I access it.

##### **Chenyu** [[00:19:16](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1156)]
Yeah. There's a weird way to deal with it. I don't really know now. Then there are functions like hash or concat that I can probably move. Also, concat is blocked by shape-changing bitcast. And I also don't know what we want to do about that. Because previously, it was only supported on tensor.

##### **Geohot** [[00:19:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1181)]
Why is cast still here?

##### **Chenyu** [[00:19:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1185)]
Because the UOp one has the dtype.vec. I can kind of move it there.

##### **Geohot** [[00:19:54](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1194)]
OK, so this is blocked on dtype.vec.

##### **Geohot** [[00:19:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1196)]
OK, well, we're just going to delete dtype.vec. And the shape-changing bitcast, I mean, the shape-changing bitcast already is not doing anything.

##### **Geohot** [[00:20:06](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1206)]
It's fine. Why can't you just copy that? Oh, we want that? I was not sure.

##### **Geohot** [[00:20:15](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1215)]
Yeah, I mean, I think it's fine. It's not anything special. Yeah, that can go in UOps. OK.

##### **Chenyu** [[00:20:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1222)]
Then other thing is we have a disk special path. Yeah. I expect another day try to move that again. It's doable. It's just also annoying. And a bunch of special paths, just one special path to another.

##### **Geohot** [[00:20:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1241)]
Yeah.

##### **Chenyu** [[00:20:42](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1242)]
So that's that. Then all the random thing. I can move it to a random mixin, like kind of JAX style, if you put the seed and size as an input. Yeah, I think that's OK. Basically turn that into a functional thing.

##### **Geohot** [[00:21:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1262)]
Well, yeah. I don't think we want to change the tensor API. But I think that tensor should call into a functional version of it. Yeah, OK.

##### **Chenyu** [[00:21:10](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1270)]
So if we want to do it properly, we need to study how JAX does that. But yeah. I think the idea is to make it functional and make the seed like an input.

##### **Nimlgen** [[00:21:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1281)]
Yeah, yeah.

##### **Chenyu** [[00:21:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1282)]
And then that should move a bunch of the inners like codes into rank.

##### **Wozeparrot** [[00:21:31](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1291)]
an input too.

##### **Chenyu** [[00:21:33](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1293)]
Is that again?

##### **Wozeparrot** [[00:21:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1294)]
is also an input.

##### **Wozeparrot** [[00:21:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1297)]
Yeah, the seed and the size, right?

##### **Geohot** [[00:21:40](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1300)]
Yeah.

##### **Wozeparrot** [[00:21:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1304)]
Yep.

##### **Chenyu** [[00:21:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1308)]
So that's the idea. Then there are even more annoying stuff, like getitem. I moved some of the normalization logic into helpers. But because tensor supports both indexing with UOp and tensor, you can probably make an analogy for UOp and index with UOp. But then you run into your issues for, do you mean symbolic getitem? Or? Something like that.

##### **Geohot** [[00:22:18](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1338)]
Yeah. I mean, we should be able to use the index UOp in more places. Yeah.

##### **Chenyu** [[00:22:26](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1346)]
Then our current index is also not that or not just that.

##### **Chenyu** [[00:22:36](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1356)]
Yeah. I think we're just... But all the UOp getitem makes something different.

##### **Geohot** [[00:22:42](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1362)]
Yeah, no. I know.

##### **Chenyu** [[00:22:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1364)]
So there's that. Yeah.

##### **Geohot** [[00:22:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1366)]
I mean, that's a big unification project. But I think the UOp one is fundamentally more correct. You see kind of where this is going, right? We can write anything you can write in tensor in UOps. And it's just so much easier to reason about this stuff in UOp land.

##### **Chenyu** [[00:23:06](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1386)]
Yeah. So if you see my `test_tensor_uop_mixing`, that test. It's basically compare applying a function on tensor and get its UOp to applying the same function to the UOp. And the output should be the same. Or subject to variance of those unique. Another annoying thing is div, because we literally mean different things. In UOp and lower, it means C div. And the upper means the Python div.

##### **Wozeparrot** [[00:23:43](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1423)]
This I don't really know. And that's pretty much it.

##### **Chenyu** [[00:23:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1433)]
That's all the tensors.

##### **Wozeparrot** [[00:23:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1436)]
Yeah.

##### **Geohot** [[00:23:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1436)]
It's nice and small now.

##### **Chenyu** [[00:24:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1443)]
So do we want a completely different metadata? Because I can restore the current behavior fairly easily.

##### **Geohot** [[00:24:14](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1454)]
You. And I'd be shocked if you could.

##### **Chenyu** [[00:24:19](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1459)]
What do you mean? You have the metadata on all the UOp.

##### **Geohot** [[00:24:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1462)]
Yep, that's great. Right until you do a single graph rewrite. And then the problem is, so there used to be a hack in graph rewrite math that would preserve the metadata when you did a rewrite. The problem is now when you do a rewrite, and not even just a rewrite of that UOp, when you do a rewrite of any UOp, anything that's downstream of that UOp is now recreated as a new UOp, right?

##### **Chenyu** [[00:24:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1484)]
Yes, and I just take the union of that input and say that's a new metadata for the new UOp.

##### **Geohot** [[00:24:50](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1490)]
But how do you know? How do you know, unless you have something like graph rewrite math, how do you possibly know?

##### **Chenyu** [[00:24:58](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1498)]
Metadata is attached to UOp, right?

##### **Geohot** [[00:25:01](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1501)]
The metadata is attached to UOp, yes. But how do you know which original UOp this corresponds to?

##### **Geohot** [[00:25:10](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1510)]
Which one? So,

##### **Geohot** [[00:25:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1513)]
think about like a long graph, right? Let's say at the top of the graph, you're putting in a const 2, you rewrite that to a const 3, right? Every single child UOp in that graph is going to be rewritten.

##### **Geohot** [[00:25:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1525)]
Okay. How do you preserve the metadata?

##### **Chenyu** [[00:25:29](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1529)]
Oh, it's just a global dict, right? UOp is all cached and shared. Yes.

##### **Geohot** [[00:25:35](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1535)]
But so when you do the rewrite, right? How do you know? How do you know to preserve the metadata? How do you build the map from the input to the output? You rewrite, right? Because all your output UOps are completely new UOps.

##### **Wozeparrot** [[00:25:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1553)]
Okay.

##### **Geohot** [[00:25:57](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1557)]
We used to solve this using graph rewrite map, but graph rewrite map was terrible and is now deleted.

##### **Chenyu** [[00:26:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1567)]
I'll check again. I just do it in the rewrite and that's it. It's fine.

##### **Geohot** [[00:26:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1573)]
You can try that. You'll hit a whole bunch of edge cases. Maybe we don't care that much. Maybe it's just a best effort thing and you can just do it in there, right? I mean,

##### **Chenyu** [[00:26:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1582)]
So one thing I know is best effort is if we decide to attach metadata to UOp through the global map or whatnot, because it's cached. So anytime if we have two operations that generate the same final UOp, you need to pick one. That was always there. That was also why one of the tests was wacky. Because the global thing conflicts.

##### **Geohot** [[00:26:50](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1610)]
Yeah. I mean, I don't really think it's the right like solution. Anyway, I think that the right solution...

##### **Chenyu** [[00:26:54](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1614)]
Yeah, so that was my question because that seems to be fairly easy to bring back, but I don't know if we want to bring it back.

##### **Geohot** [[00:27:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1622)]
Well, I think that before we answer that question, we may want to bring something like it back. But I think the next question to ask after the metadata project is, so we have this function now called apply UOp in tensor. Tensor should basically no longer inherit from mixins.

##### **Geohot** [[00:27:24](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1644)]
Right now, tensor is a subclass of OpMixin.

##### **Geohot** [[00:27:29](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1649)]
Subclass of OpMixin, but we should remove that and we should create like a forwarder. And then this forwarder creates functions.

##### **Chenyu** [[00:27:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1661)]
Yeah. If you're something like that, it's how we ultimately want to do that.

##### **Geohot** [[00:27:47](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1667)]
Yeah. But like just think about how beautiful the graph will be, right? Because function should already completely work with backwards pass. That's no problem.

##### **Wozeparrot** [[00:27:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1676)]
How does it work with assign?

##### **Geohot** [[00:28:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1680)]
Well, you already can't differentiate assign.

##### **Chenyu** [[00:28:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1685)]
Yeah, assigns are also an issue even in a current method. But anyway, I see the grand idea.

##### **Geohot** [[00:28:12](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1692)]
Yeah, yeah, there's no, I mean, there's no sign. It's not like the function thing is just a pure, it's a pure substitution, right? That's why I split it into function and call. Function is stateless.

##### **Geohot** [[00:28:28](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1708)]
Like I actually want to enforce that. I actually want to enforce that function can't have store inside of it. So anything that uses op function has to be pure. Is that true now?

##### **Wozeparrot** [[00:28:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1724)]
Maybe.

##### **Geohot** [[00:28:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1729)]
Okay. Well, that goal is to make that true.

##### **Geohot** [[00:28:51](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1731)]
So yes, the goal is to make function pure and then to make all these things pure. And then if you want to do something like assign on a tensor. Yeah. I mean, that's not going to be the function that has to be in the big graph.

##### **Wozeparrot** [[00:29:06](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1746)]
Okay.

##### **Chenyu** [[00:29:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1747)]
Oh, anyway, from my end, I was. Probably this week, because more on the render than doing, we should have like very little that. Okay.

##### **Wozeparrot** [[00:29:20](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1760)]
Yeah.

##### **Geohot** [[00:29:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1765)]
The removal of that, the removal of tensor subclassing OpMixin and then just having a forwarder. It's kind of like the final.

##### **Geohot** [[00:29:35](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1775)]
Like, you know, like I said in my, like I said in my message, these, these, these, these things.

##### **Geohot** [[00:29:39](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1779)]
These rabbit holes are, are deep, but there's nothing beyond. Okay. Another big project after the vec project is going to be the removal of dtype from UOp. So UOp is just going to have op, source, and arg. Great. Yeah.

##### **Chenyu** [[00:30:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1802)]
They can move a lot of the current broadcast type logic.

##### **Geohot** [[00:30:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1808)]
Yeah. Yeah. Oh yeah. Broadcast dtypes and broadcast shape should move to the UOp dtype. Resolver broadcasting of shape should move to the shape resolver. And we can have passes which add them explicitly if it's needed, but. We can imagine a pass that just adds the reshape, expand, or cast, but.

##### **Chenyu** [[00:30:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1832)]
Yeah. Another interesting thing at, or maybe around that time would be the actual weakint. Currently it's slightly annoying because for the index one, we really want something that represents an infinite-width integer. But if you think about it, anything that adds two should upcast to the same infinite-width integer, but we also want like a weak one that's below everything and turns into that if we have to turn it into any concrete int. Basically in this hierarchy, we want one that is very low and one that is very high. Currently we are mixing the two in this weakint.

##### **Geohot** [[00:31:24](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1884)]
I don't follow this.

##### **Chenyu** [[00:31:26](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1886)]
Anyway, it's, it's. So now we have some rules saying, and the index or the weakint or anything we use for indexing that matches actual int, what's the type of that? We have rules, but that rule is in the rewrite, not in a dtype promote logic.

##### **Geohot** [[00:31:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1909)]
Oh, I see. Yeah. Yeah. No, I don't like that. I also don't like, I think I want to move. So right now we have like DEFINE_VAR, which has a min and a max. I think we just get rid of that min and the max. And then if you want min and max, you can just like write them explicitly as UOps, which are kind of good anyway.

##### **Geohot** [[00:32:06](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1926)]
Okay. Okay.

##### **Geohot** [[00:32:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1927)]
So just like, yeah, I mean, this deals with a lot of the, like, like indexing can go out of range stuff. Just don't let indexing go out of range instead of like making DEFINE_VAR, instead of making it a promise, just make it explicit. It's not like it's slow.

##### **Nimlgen** [[00:32:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1950)]
Okay.

##### **Chenyu** [[00:32:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1952)]
Oh, anyway, that's more further down and we can, we can move on. Another big thing is a JIT and ExecItem refactor.

##### **Geohot** [[00:32:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1965)]
Yeah.

##### **Nimlgen** [[00:32:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1965)]
So I removed ExecItem. So now both JIT and schedule use `run_linear`. So I honestly remove all of the runners as well. So I'm just on the path to remove CompiledRunner.

##### **Wozeparrot** [[00:33:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1987)]
Yeah.

##### **Geohot** [[00:33:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1989)]
Instead of CompiledRunner, you have a, like a, like a, a, UPat match.

##### **Wozeparrot** [[00:33:19](https://www.youtube.com/watch?v=z0SgQk_yySo&t=1999)]
What file is that?

##### **Geohot** [[00:33:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2003)]
I mean, it's all in realize.py.

##### **Geohot** [[00:33:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2010)]
So you have this `pm_exec` thing, which is going to replace everything.

##### **Nimlgen** [[00:33:33](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2013)]
Yeah. Yeah. Cool. I mean, it's currently called it, but I already refactored. I removed the ProgramSpec. It's now ProgramInfo. It's mostly renamed, but it also sits as the argument to the program.

##### **Geohot** [[00:33:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2029)]
No, I'm, I'm, I'm really liking the direction this refactor is going. Uh, I think `pm_exec` is very clearly understandable. I think it's way more understandable than what existed before.

##### **Geohot** [[00:34:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2043)]
Um, yeah. `pm_beam`.

##### **Geohot** [[00:34:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2045)]
I mean, these things are finally kind of in the right place. Uh, I know that Comma has a regression with the no locals thing.

##### **Nimlgen** [[00:34:14](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2054)]
Yeah. Um, I'll merge this today. Already have PR. So actually no locals will be also like rewrite rule for now and the `compile_linear`.

##### **Wozeparrot** [[00:34:31](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2071)]
Yeah.

##### **Nimlgen** [[00:34:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2072)]
Cool.

##### **Geohot** [[00:34:33](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2073)]
Uh, yeah, no, but yeah, great. Great work on this. I'm, I'm very happy with this. This feels like one of those projects that, uh, like one of those last, really one of the last legacy systems that everything's kind of UOp. Um, yeah, I mean, I think then I think kind of the next thing is going to be starting to move more and more of the drivers, uh, into UOps. I think we need something like a wait.

##### **Wozeparrot** [[00:35:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2107)]
Can I repeat what I'm... wait. Yeah.

##### **Geohot** [[00:35:10](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2110)]
So like, wait, yeah, yeah, yeah. Yeah. Right. Like think about, think about moving these. So currently you're like compiling to PM4, um, in the HCQ graph stuff.

##### **Wozeparrot** [[00:35:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2123)]
Yeah.

##### **Geohot** [[00:35:24](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2124)]
Um, like that should kind of move to UOps too.

##### **Nimlgen** [[00:35:28](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2128)]
Yeah. Yeah. So also, yeah. Uh, so actually graph is also like currently implemented. Like in the old way, they just use linear instead of JIT cache. But yeah, I, yeah. So ideally they should just reuse the same, I mean the same runtime functions.

##### **Wozeparrot** [[00:35:50](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2150)]
Um, yeah, okay.

##### **Nimlgen** [[00:35:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2152)]
I mean, it just was really annoying because like, it's really hard to add like the decoder into the HCQ graph now, because there is a lot of logic you just need to copy and paste into the HCQ graph. So yeah, I'll make this to be shared. What do you mean, add the decoder? I mean, we have the decoder, HEVC decoder for NV. And it's not an HCQ graph right now. Basically, it's possible to do that, but you basically need to copy all this logic into it. Basically, all this code in the HCQ graph.

##### **Geohot** [[00:36:38](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2198)]
Yeah, I'm talking about like AMD ComputeQueue. Yes. I'm talking about like AMD ComputeQueue becoming a UOp graph. And we effectively have a renderer. It's a renderer, right?

##### **Geohot** [[00:37:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2222)]
We have a renderer which takes the UOp graph and converts it into the literal bytes that get pushed to the queue for the GPU.

##### **Wozeparrot** [[00:37:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2233)]
Yeah. It's a project.

##### **Geohot** [[00:37:20](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2240)]
You know, this is not expected to be done in like a week or anything. But yeah, I think like AMD ComputeQueue and AMD CopyQueue become renderers for the graphs. Right? Like CopyQueue is a renderer that targets the SDMA engine. ComputeQueue is a renderer that targets the MEC.

##### **Nimlgen** [[00:37:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2266)]
Okay. Yeah. Actually, then I thought about that. I would think that we just have some, like, a context per HCQ device. And basically all these lowering will be just rewrite rules. You basically have these ops copy. And instead of like going to execute them, you just like, yeah, in a device-specific way, convert them to bytes. And after that, you just execute this with some custom function or something like that. Yeah.

##### **Geohot** [[00:38:20](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2300)]
I mean, this gets fun to think about. Like where I first realized that this was obviously the path was on the WebGPU side. Because on WebGPU, like the thing that you want to output is not, sure, okay, I have these bunch of functions, right? They're WebGPU kernels. But the thing that I eventually want to output for WebGPU is a JavaScript file. Right? So then you have a renderer, which can render a WebGPU run graph into a JavaScript file. And that's effectively the same thing as the, like, ComputeQueue renderer. But instead of rendering into JavaScript, you render it to the MEC. Yeah, that's kind of it. the final form of that. But I do think, and I'm probably deluding myself, but I do think these things are getting really close to the final form. And have I said this for many years? Have I always said that we're close to the final form and we never are?

##### **Chenyu** [[00:39:15](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2355)]
It's probably inch half every year or something.

##### **Nimlgen** [[00:39:20](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2360)]
I don't know.

##### **Chenyu** [[00:39:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2361)]
Surely what? You probably get it. Closer and closer.

##### **Chenyu** [[00:39:28](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2368)]
Yeah, yeah, yeah. And yes, that was there probably three years ago.

##### **Geohot** [[00:39:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2374)]
Well, I just don't want to fall for some halting problem crap here, where it's like one of these things where you're always like, oh, it's going to halt, oh, it's going to halt, and it never will. But I think it does.

##### **Chenyu** [[00:39:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2388)]
I think we have traversed a lot of bad designs. So if we believe the ultimate is elegant solutions there,

##### **Chenyu** [[00:39:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2396)]
we are certainly closer.

##### **Geohot** [[00:40:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2400)]
Yeah.

##### **Geohot** [[00:40:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2402)]
I mean, we've definitely traversed a lot of bad designs. It's just a question of is the bad design space so massive that we haven't even touched exploring all of it yet? Or we're actually kind of really

##### **Wozeparrot** [[00:40:16](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2416)]
getting to the end? Because if it's the former, then

##### **Geohot** [[00:40:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2425)]
this doesn't work. But I don't think I don't think it is. I think these things are like the UOp graph is this final form of ultimate elegance that there's nothing better than it. And then it still doesn't answer the search question. The search question is, is probably going to define a huge next era of the company, right? The question then to ask is like, oh, yeah, how do we find the best possible graph? Well, good luck. But like, at least we've defined the language. And I think we are getting close to defining a complete language that's kind of optimal.

##### **Chenyu** [[00:41:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2468)]
Yeah, that makes sense.

##### **Chenyu** [[00:41:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2469)]
I mean, search acts on your state of your language, right? So once you have a couple of compact language, then you worry about the search, but not the other way around.

##### **Geohot** [[00:41:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2481)]
Yeah. And I think that this is a lot of conversations with GPT 5.5 about like, if this works or not and who AI search is really going to benefit, like who's going to benefit from AI? It's, you know, it's interesting seeing all the things on Twitter now where people are saying like, remember that time we all used AI to code and everyone now just codes by hand again?

##### **Nimlgen** [[00:41:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2506)]
That's a lot of work.

##### **Geohot** [[00:41:47](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2507)]
I posted this thing I liked in Comma Slack, about how like, the LLMs have created this simulacrum of knowledge work. And only if your target is truly perfect, right? If there's any amount where your target can just, the answer can just look good, but be wrong, then the LLMs will find that. But if we can really define a tight, compact language, and then the other thing that GPT was really saying what the make or break would be is if the LLM generated or the LLM searched for graphs are human understandable or not. And it's super important that they are. If at the end of what we've done, like one of the problems with vibe coding is you end up with this huge repo that nobody can understand. It's useless, totally useless. It's useless to LLMs too, because if humans can't understand it, LLMs can't understand it. But if the LLM could pour tons of compute into finding small graphs that implement things fast, well, that works. But that's a question of really making sure the language is all correct.

##### **Wozeparrot** [[00:43:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2583)]
So I think LLM search benefits us way more than anybody else, but we'll see. Okay. Anything else from the origin?

##### **Nimlgen** [[00:43:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2605)]
No, I think this week I'll remove CompiledRunner. I just still need to look into the TinyF machines issues. And yeah, probably we'll add this feature for LLM.py. It's not a pipe, but for LLM to just save the compiled and save the graph.

##### **Chenyu** [[00:43:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2632)]
Oh, by the way, are we doing the LLaMA training on two-machine thing or we're not doing that?

##### **Geohot** [[00:44:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2642)]
I think what?

##### **Wozeparrot** [[00:44:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2645)]
Okay.

##### **Geohot** [[00:44:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2648)]
Oh, yeah, I don't think.

##### **Wozeparrot** [[00:44:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2649)]
Yeah, but I'm not going to get back to us by May 11th.

##### **Geohot** [[00:44:12](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2652)]
We're not going to have two machines. I see. Okay.

##### **Geohot** [[00:44:16](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2656)]
You know, we can't even train on DA4, can we? Yeah, okay.

##### **Wozeparrot** [[00:44:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2661)]
Yeah, that's fine.

##### **Geohot** [[00:44:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2662)]
DA3 doesn't break.

##### **Wozeparrot** [[00:44:27](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2667)]
Okay. Our next is this.

##### **Qazalin** [[00:44:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2674)]
Yeah, so we reproduced Kimi's result on M3. And the CLI got a little bit cleaner. In general, just better defaults from watching how the LLMs use it. I think this sprint, I want to move to the bigger models.

##### **Geohot** [[00:44:59](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2699)]
Is that stuff merged that fixes the overlap of the WMAs?

##### **Qazalin** [[00:45:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2705)]
I merged the stuff that discovers the exact pipes. So it turns out. I can't see the exact pipes.

##### **Nimlgen** [[00:45:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2713)]
I can't see the exact pipes.

##### **Qazalin** [[00:45:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2713)]
I couldn't find a way for the WMAs and the VALUs to ever execute at the same time to overlap. Even on RDNA4.

##### **Geohot** [[00:45:26](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2726)]
Okay, yeah, it looks pretty good now.

##### **Wozeparrot** [[00:45:31](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2731)]
I don't think there's any overlap.

##### **Qazalin** [[00:45:35](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2735)]
Oh, God, there is overlap. There is overlap. I have it. On RDNA4.

##### **Geohot** [[00:45:40](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2740)]
How about RDNA3? RDNA4.

##### **Qazalin** [[00:45:43](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2743)]
No. RDNA3 never overlaps.

##### **Geohot** [[00:45:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2745)]
Yeah, I mean, RDNA4 still has that bug that we have to find.

##### **Qazalin** [[00:45:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2749)]
I tried very hard for the RDNA4.

##### **Geohot** [[00:45:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2753)]
Find it, and you can't?

##### **Qazalin** [[00:45:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2755)]
I am 90% sure it's a hardware bug because AMD's decoder reports the same.

##### **Geohot** [[00:46:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2765)]
Yeah, that sounds like a bug in AMD's decoder that we're also relying on. I would be shocked if it was a hardware bug.

##### **Qazalin** [[00:46:12](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2772)]
I'll try more. The deltas look correct. Like, I have 10 packets. I have it down to, like, a pickle that has 10 packets, and Claude couldn't find it after, like, two hours. Like, what the bug is.

##### **Geohot** [[00:46:29](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2789)]
Yeah, well, you know, Claude's an idiot.

##### **Qazalin** [[00:46:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2794)]
I mean, like, I look at it, too, but, like, the numbers look...

##### **Geohot** [[00:46:39](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2799)]
Yeah, I mean, it's possible it's a hardware bug.

##### **Qazalin** [[00:46:42](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2802)]
I don't know.

##### **Geohot** [[00:46:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2804)]
Do you have, like, a clean repro? It's only, like, one cycle. If it's a hardware bug, let's write it up and complain to AMD.

##### **Qazalin** [[00:46:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2815)]
Yep. It's also non-deterministic, which is really annoying. But if you get lucky, you can reproduce it very easily by just, like, issuing WMAs in a loop. No RAM access.

##### **Geohot** [[00:47:10](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2830)]
Yeah. If you can write a small repro that uses AMD... Yeah. ...and then you can use AMD's decoder that reproduces it, then, yeah, I think we can, like, submit a bug report.

##### **Geohot** [[00:47:20](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2840)]
Right.

##### **Nimlgen** [[00:47:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2841)]
Yeah. I'll do that.

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2844)]
Yeah, the other thing... I think you guys are both having this problem with putting the contiguouses in on function, the extra contiguouses.

##### **Wozeparrot** [[00:47:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2854)]
Yes.

##### **Wozeparrot** [[00:47:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2857)]
My issue is that function makes an explicit copy for outputs. Yeah. For outputs of the function, to save, it makes params and then does a store into the param. And then this does an extra...

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2872)]
This creates a copy kernel.

##### **Wozeparrot** [[00:47:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2876)]
Interesting. Can you look into that? Is that...

##### **Geohot** [[00:48:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2888)]
So the issue is that the store is contiguous. Yeah. Yeah. Or something is making it contiguous.

##### **Qazalin** [[00:48:18](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2898)]
Hmm. I think I have the opposite problem. The inputs are contiguous, and that's very odd.

##### **Geohot** [[00:48:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2905)]
The inputs being contiguous, I understand why I wrote that. And that's... Yeah. But... By the way, what I want you to work on this week is using any of this stuff.

##### **Geohot** [[00:48:36](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2916)]
We need to make anything we can do to make MLPerf faster.

##### **Wozeparrot** [[00:48:42](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2922)]
Mm-hmm. So, yeah.

##### **Nimlgen** [[00:48:43](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2923)]
So, yeah.

##### **Geohot** [[00:48:43](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2923)]
I want you to get LLMs using this stuff, whether it's LLMs or human, or we just got to make this faster. You know, 245 is good. 230 is better. 215 is great.

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2936)]
If you hit 215, that's like competitive with their thing.

##### **Wozeparrot** [[00:49:04](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2944)]
Wozeparrot, did you use the profiler so far?

##### **Geohot** [[00:49:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2949)]
Yes. I requested that it prints per-step times instead of sum.

##### **Wozeparrot** [[00:49:15](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2955)]
Instead of sum.

##### **Geohot** [[00:49:23](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2963)]
It should. Yeah.

##### **Wozeparrot** [[00:49:27](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2967)]
Nimlgen, do we also have any tricks we can do to juice it a little? I can take a look into these.

##### **Wozeparrot** [[00:49:40](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2980)]
Yeah. Let's... I don't know if it's possible. We're hitting PPT limit already. Like, all of our matmuls hit that. Like, that's why it's so much faster. We push into power limit.

##### **Geohot** [[00:49:50](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2990)]
We push into power limit. Okay. Yeah.

##### **Wozeparrot** [[00:49:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2993)]
Yeah.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=z0SgQk_yySo&t=2994)]
Anything we can do? Anything that we can do to boost this? Let's go. If we can beat 1:27, that's incredible.

##### **Wozeparrot** [[00:50:04](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3004)]
That's the worst time on the board right now. But, yeah. Any copies we can get? That's a pretty good question. I don't know what I can avoid or any...

##### **Nimlgen** [[00:50:19](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3019)]
Yeah.

##### **Wozeparrot** [[00:50:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3021)]
Yeah. No. I want this.

##### **Geohot** [[00:50:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3022)]
I want this viz profiler stack working on LLaMA and working to make LLaMA better, and working to autodiscover bugs. Let's figure out why it's slow, what we're doing that we don't have to do.

##### **Geohot** [[00:50:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3034)]
All that.

##### **Qazalin** [[00:50:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3037)]
Cycle time is 2 minutes. So I think it should be.

##### **Geohot** [[00:50:40](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3040)]
Cool. Yeah. I mean, it's 2 minutes, but you can also do LLaMA layers and make it faster. Yeah, I mean, we don't have to.

##### **Geohot** [[00:50:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3049)]
We don't have to do the full thing. Yeah, we don't have to do the full thing. Just do LLaMA layers. Get a fast one. Get a representative one in 30 seconds.

##### **Wozeparrot** [[00:50:58](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3058)]
And then we can throw the best files we can at it. Okay, yeah, it's kind of deliverable for this.

##### **Geohot** [[00:51:18](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3078)]
Sounds good.

##### **Wozeparrot** [[00:51:20](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3080)]
Anything else? I guess that's it.

##### **Qazalin** [[00:51:28](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3088)]
The custom kernel issue with contiguous inputs I think is pretty obvious. They have to sort of reason about walking the graph back to the point that they want it to do fusion. Because it can be looking multiple files. It can be in different layers.

##### **Wozeparrot** [[00:51:50](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3110)]
And if they .

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3111)]
That's not obvious to me.

##### **Wozeparrot** [[00:51:54](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3114)]
Go ahead.

##### **Geohot** [[00:51:59](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3119)]
I mean, we should just be seeing if we have

##### **Geohot** [[00:52:01](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3121)]
any good results. We should be looking at the types of kernels at the end that are just stupid copy kernels and why we still have stupid copy kernels.

##### **Geohot** [[00:52:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3128)]
We obviously can't fuse inside the custom function. Right? Like, we can't.

##### **Geohot** [[00:52:17](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3137)]
The custom function is a barrier. The only thing that we can maybe fix here is, is there any place where that contiguous is actually

##### **Geohot** [[00:52:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3145)]
just creating a dumb copy of something that's already contiguous?

##### **Wozeparrot** [[00:52:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3152)]
Like, if that kernel is actually doing something, then there's nothing we can do. Yeah.

##### **Qazalin** [[00:52:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3161)]
I mean, how many of these are solvable by storing them transposed?

##### **Wozeparrot** [[00:52:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3173)]
Yeah.

##### **Geohot** [[00:52:54](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3174)]
But even that requires changes to the custom kernel, right? How many in LLaMA, how many dumb copies do we still have? How many copies that actually do nothing are we still doing? Why?

##### **Qazalin** [[00:53:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3189)]
I think most of them are because of the GEMM, because the GEMM requires transpose.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3194)]
But a transpose is not a dumb copy.

##### **Wozeparrot** [[00:53:20](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3200)]
I mean, sort of like a pure transpose.

##### **Qazalin** [[00:53:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3202)]
OK, dumb copy. I'll get that.

##### **Geohot** [[00:53:26](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3206)]
Yeah. How many actual completely dumb? A transpose is not a copy, right? How many actual dumb? Yes. I'm just literally copying these bytes for no reason.

##### **Geohot** [[00:53:37](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3217)]
We have a GEMM that doesn't require a transpose. How much would that help?

##### **Qazalin** [[00:53:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3226)]
HIP kernels requires because of how the FP8s are structured.

##### **Wozeparrot** [[00:53:53](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3233)]
Yeah. OK. Maybe there's something behind them. They also don't have parameters for a transposed FP8 GEMM.

##### **Geohot** [[00:53:59](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3239)]
I looked into this a little bit.

##### **Nimlgen** [[00:54:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3242)]
I don't know.

##### **Wozeparrot** [[00:54:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3243)]
How many custom kernels do we now have?

##### **Nimlgen** [[00:54:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3248)]
I could count them all.

##### **Geohot** [[00:54:10](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3250)]
Look at fused AdamW kernel.

##### **Wozeparrot** [[00:54:12](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3252)]
All right. Yeah. 106, I think.

##### **Nimlgen** [[00:54:16](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3256)]
OK.

##### **Wozeparrot** [[00:54:17](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3257)]
106 unique. But I haven't merged yet, just because it's really ugly right now.

##### **Geohot** [[00:54:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3262)]
Clean it up before I merge it.

##### **Nimlgen** [[00:54:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3265)]
OK.

##### **Geohot** [[00:54:30](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3270)]
Let's move on.

##### **Chenyu** [[00:54:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3272)]
We have five minutes left. Comma seems to be not very happy about a break that happened. What happened?

##### **Geohot** [[00:54:42](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3282)]
The JIT refactor.

##### **Chenyu** [[00:54:43](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3283)]
Yeah. Yeah. This was discussed.

##### **Geohot** [[00:54:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3286)]
Yeah. Yeah. It's this no locals thing, so they're going to be frustrated about that.

##### **Geohot** [[00:54:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3292)]
Can you make sure that it gets updated for them?

##### **Geohot** [[00:54:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3296)]
Yes.

##### **Nimlgen** [[00:54:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3296)]
Right.

##### **Wozeparrot** [[00:55:00](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3300)]
Is there a way to do this? Is there a way that we put slightly more stuff

##### **Chenyu** [[00:55:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3305)]
in our task?

##### **Chrism** [[00:55:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3307)]
Yeah. So the thing we need to do is support their new compile. They have a new compile script that they use for some stuff. And then they still use compile3 in some places. I was kind of hopeful that they were going to stop using compile3 altogether and use their new compile infrastructure entirely. I don't know if this is going to happen, so I need to bug Arman and see if we need to support both of these. But we definitely should be testing this. This bug in particular, this no locals issue, is pretty weird because it only happens when you load the pickle in the same process. But yeah, we definitely should be testing the way

##### **Wozeparrot** [[00:55:51](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3351)]
that they expect to use it.

##### **Nimlgen** [[00:55:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3355)]
Yeah.

##### **Wozeparrot** [[00:56:01](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3361)]
OK.

##### **Chenyu** [[00:56:02](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3362)]
I think if it's easy, then we can put that in our test. If it's really convoluted, then we can discuss.

##### **Chrism** [[00:56:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3369)]
I think right now, the new compile script depends on stuff in openpilot. So that makes it a little harder. But Arman said he was going to remove the dependency on openpilot. And then we should be able to just use that.

##### **Chenyu** [[00:56:25](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3385)]
Yeah. I mean, there's a limit for what we reasonably can maintain.

##### **Nimlgen** [[00:56:31](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3391)]
Yeah.

##### **Chenyu** [[00:56:31](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3391)]
There are actual device runtime tests we already cannot run. That's why previously, when I was trying to make a speed fix, someone needs to run it for me. And that doesn't really help.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3409)]
All right.

##### **Chenyu** [[00:56:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3409)]
Which we can't run? Because they care about the three models running concurrently on the device with all the things running. And the actual end-to-end time of running of that is what they really care. So even if I say, OK, in benchmark, I improved this, it's not actually accurate. And that makes it really annoying.

##### **Chrism** [[00:57:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3428)]
Yeah. I don't know. For some reason, I was under the impression that they were going to be running stuff on the CPU now. And it wasn't going to be an issue. But apparently, that's not true. So I don't really know what's going on with that.

##### **Chenyu** [[00:57:18](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3438)]
I think the bottom line is the actual features we support, we should try very hard to not regress those. So things like no locals. Oh, yes. I understand it's a hacky flag. But regressing those behaviorally is really bad. The speed issue, I think that's something we can discuss with Comma directly more,

##### **Chenyu** [[00:57:40](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3460)]
as what's reasonable to maintain.

##### **Chenyu** [[00:57:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3464)]
Yeah, for sure.

##### **Chrism** [[00:57:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3466)]
Yeah.

##### **Geohot** [[00:57:46](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3466)]
The other thing that they're worried about,

##### **Chrism** [[00:57:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3468)]
which I'm going to fix, is the runtime dependency on the internet for AMD. This isn't really an issue for anyone else, because most people don't delete their cache directories every reboot. But we have a solution for that.

##### **Wozeparrot** [[00:58:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3485)]
So it shouldn't be an issue.

##### **Geohot** [[00:58:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3493)]
I mean, going to libfirmware is better anyway,

##### **Geohot** [[00:58:15](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3495)]
because if people have libfirmware, we should check the hash for that.

##### **Chrism** [[00:58:19](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3499)]
Yeah, yeah. You mentioned this. But if they update, if you have an older version of libfirmware or Linux firmware, then you might be loading the wrong firmware, or maybe there was some update that got released that we want to have.

##### **Geohot** [[00:58:34](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3514)]
Yeah, we should push the hash on the thing. We should check the hash for the version we downloaded, too. Yeah.

##### **Wozeparrot** [[00:58:41](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3521)]
Fast. OK.

##### **Chenyu** [[00:58:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3524)]
I think let's see, short term, let's try to get it in a good state so that they can upgrade a version or whatnot. I think this happens every time we make a big refactor and a lot will complain. And if we believe we are getting closer and this is the last piece, then I won't worry too much about it. Just making sure.

##### **Geohot** [[00:59:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3545)]
Yay, last refactor.

##### **Chenyu** [[00:59:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3548)]
We'll see.

##### **Chrism** [[00:59:09](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3549)]
I think this was especially bad, because they were simultaneously doing a big refactor of how they used tinygrad.

##### **Chenyu** [[00:59:14](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3554)]
No, this is great, because then they cannot fully blame us. Last time, they did nothing for two months, and it regressed super bad. So OK. OK. I think let's just try to be supportive and at the end learn something, since this would be also potential issues for future users, and see how we can remove bad tests and add actually useful tests to our benchmark for them. I think that would be nice.

##### **Nimlgen** [[00:59:45](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3585)]
Cool.

##### **Chenyu** [[00:59:48](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3588)]
George, can you see what's the state for LLM, whatever models we want to add support to and things like that?

##### **Geohot** [[00:59:56](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3596)]
Yeah. So B1TG says it's got Kimi running. Great. So yeah, that's exciting. I mean, Kimi 2.6 is great. Actually, I realized this coming back here, talking to the Comma people, what I've been doing for the last few months, which is learning all about how to run LLMs and learning all the new tricks. So yeah, it's been cool. So yeah, Kimi is working. I don't know how he did the sharding. The sharding is kind of annoying, because you have to shard. You want to shard at the GGUF level. You don't want to shard, maybe for Kimi it's a little bit different, but you don't want to shard after, because you want to make sure it stays in 4-bit or whatever. So yeah, I mean, supporting Kimi would be great. Are there PRs for other people who want to support other things? I think we got most of them.

##### **Wozeparrot** [[01:00:49](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3649)]
The other thing we don't want to do is DeepSeek for now.

##### **Geohot** [[01:00:52](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3652)]
Yeah. What else to support? I feel that's a kitchen sink. Yeah, yeah, yeah. Don't waste time on DeepSeek for now. It's even questionable. I think we should probably support GQA.

##### **Wozeparrot** [[01:01:03](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3663)]
I do think that Kimi 3 would be very similar.

##### **Chenyu** [[01:01:07](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3667)]
We will see when we get there.

##### **Wozeparrot** [[01:01:10](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3670)]
Same attention residual design as MLA.

##### **Geohot** [[01:01:15](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3675)]
Yeah, MLA itself doesn't seem that bad. It's just...

##### **Wozeparrot** [[01:01:21](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3681)]
The sparse attention is...

##### **Geohot** [[01:01:22](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3682)]
Yeah. I mean, it's just they have so much weird stuff in there. That I think of the like four weird things they have, one of them is going to stay around.

##### **Chenyu** [[01:01:32](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3692)]
I think this is very similar to our early logics for what to include in the end. I think if a trick is used by two or three labs, then we incorporate those.

##### **Geohot** [[01:01:44](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3704)]
I think that's right. Yeah. Okay. Yeah. I mean, yeah. I don't know. I don't know why exactly we don't support Gemma 4. I mean, that's the other one.

##### **Geohot** [[01:01:55](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3715)]
I don't know if we're missing anything in particular for it, or it's just... Okay. Anyway, leave that to you.

##### **Nimlgen** [[01:02:05](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3725)]
Cool. Okay.

##### **Chenyu** [[01:02:08](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3728)]
Thank you, everyone. So next week meeting will be moved back to Monday.

##### **Chenyu** [[01:02:13](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3733)]
And we'll see you next week. Bye bye.

##### **Geohot** [[01:02:16](https://www.youtube.com/watch?v=z0SgQk_yySo&t=3736)]
Bye.
