# 2026-06-15 Meeting

### Meeting Agenda

**Time:** new meeting #24, 6/15 9am Monday San Diego time
- company update
- hcq2 jit
- CI updates
- llama training
- VIZ llama schedule
- const mixin
- new style renderer
- bounties, issues, comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=t4-yUBzsr-I)

### Highlights

- **[Company Update](#geohot-000006)**: Sales remain strong, with roughly another $200k in wires last week; Geohot emphasized that progress still feels slow, but tinygrad is moving toward clearer specs and reality-tested LLaMA training.
- **[HCQ2 Driver Spec](#geohot-000233)**: HCQ2 is coming along; the immediate goal is making it legible to the UOP graph, then cleaning it up, with new UOPs added to the spec.
- **[CI Docker Investigation](#chrism-000424)**: Chrism tried packaging CI dependencies into Docker; the image reached about 3GB, mainly due to Intel OpenCL CPU runtime and multiple LLVM installs, with only about 700MB actually needing download.
- **[CI Speed and Flakiness](#chrism-000922)**: Slow CI setup is partly from installing full testing dependencies like TensorFlow and ONNX; OpenCL tests remain slow and flaky, with segfaults likely coming from the runtime or compiler.
- **[OpenCL Runtime Alternatives](#geohot-001628)**: The team discussed moving away from Intel OpenCL toward POCL or Rusticl, especially if Intel’s compiler is causing wrong outputs or instability on AMD CPUs.
- **[MXFP8 and LLaMA Training](#wozeparrot-001817)**: MXFP8 was merged and improves DP convergence somewhat, but MP convergence is still about 300 steps slower, possibly from a bug or numerical issue.
- **[MP Debugging Plan](#geohot-001947)**: Geohot suggested starting with two GPUs to isolate the MP convergence issue; Chenyu recommended logging gradient statistics such as grad norm and gradient max.
- **[7B and 405B Training Timeline](#wozeparrot-002157)**: Wozeparrot hopes to kick off another 7B run by the end of the week, while the 405B deadline is believed to be around October.
- **[VIZ LLaMA Schedule](#qazalin-003051)**: The LLaMA VIZ run improved from about 11,000 kernels to 9,000 and remains around 2h50m; the goal is to match or beat AMD by removing unnecessary copies and scheduler overhead.
- **[Kernel Count Reduction](#qazalin-003218)**: Around 2,000 extra kernels come from shrink-then-copy patterns that create unnecessary contiguous operations; fixing this should reduce total kernels by roughly 20%.
- **[Custom Kernel Contiguous Cleanup](#geohot-003336)**: Geohot said user-inserted `contiguous` operations around custom kernels should not exist; they should be inserted only after scheduler resolution.
- **[Const and Function/Call Cleanup](#chenyu-003828)**: Chenyu is close to removing `const unique` and is testing changes around anonymous buffers, embedded clones, and function/call behavior without breaking LLaMA.
- **[New Renderer API](#geohot-005226)**: All renderers now take the new-style API; pointer dtype and vec dtype are gone from codegen output, `shrink` can be used inside programs, and buffers are now represented as either external `param` or internal `buffer`.
- **[Summer of Spec Tightening](#geohot-010049)**: Geohot closed by framing the next phase as “the summer of spec tightening,” aiming for a solid foundation where every part of the system has a clear reason.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=0)]
Let's start with company update.

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=6)]
I just noticed that test gem no longer actually tests a gem because the contiguous is being ignored. But that's not really company related. I just noticed this. I'm like, why is this happening? Sales are good. We sold a lot of tiny boxes. We made like another, you know, like another like 200k wires last week. I don't know. Everything just feels slow as usual. But I don't really know who's making faster progress on this stuff. It seems like we live in a world where this like agentic coding crap has elevated the temperature of everything to some crazy high point. And then like you look at what's actually been produced. Like, can you name a software project that's been produced since like December? When this all started? I'm like, not really. So, yeah, it's all slow going, but maybe it just feels slow going. That's how this is all. This is all like the trick of AI. It's like you don't know if am I being reward hacked? So, yeah, no, I think we're proceeding toward a spec. A lot of things basically look like proceeding toward a spec. If what you're working on doesn't look like a spec, then you're not. If it doesn't look like proceeding toward a spec, then we should fix that. Because that's kind of like, OK, we're going to have mixins as an isolated thing. We're going to have the program spec as an isolated thing. We're going to have a range of my spec that figures out how to remove these E kernels. We're going to have a set of tests that are well thought out. And we're going to do the LAMA contract to prove that we can actually do something. And this is like touching grass, right? I think it's more important. Than ever to stay in contact with reality. And reality is training large LLMs.

##### **Chenyu** [[00:02:08](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=128)]
So, yeah, let's come out there. Oh, sounds good.

##### **Chenyu** [[00:02:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=137)]
I think in the emergency he's traveling. So he puts the updates in HCQ drivers. I think there was added just support and something. Something is still missing.

##### **Geohot** [[00:02:33](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=153)]
Yeah, it seems like it's coming along nicely. He said profiling is missing. Yeah, I mean, there's going to be a whole set of cleanups to HCQ2 as well. But at least the first step is just making it visible to the UOP graph. Like making it legible. Like we make it legible to the UOP graph. And then we. Clean it up.

##### **Chenyu** [[00:03:02](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=182)]
Like get at her. Is that real? I don't really know. What does that do?

##### **Geohot** [[00:03:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=191)]
But, yeah, no, we should have him. If he was here, my advice would be I'll just post this in HCQ drivers. I'm like, can you add all the new UOPs you are using to the spec?

##### **Flata** [[00:03:23](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=203)]
Yeah. Yeah. Yeah.

##### **Chenyu** [[00:03:30](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=210)]
I will spec the document. The.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=213)]
Yeah.

##### **Chenyu** [[00:03:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=216)]
It's pretty complete now. At least for.

##### **Geohot** [[00:03:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=224)]
Like all the code stuff actually matches the spec.

##### **Geohot** [[00:03:48](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=228)]
Like everything that's going into everything that's going into the renderers is now is now fully in the spec.

##### **Chenyu** [[00:03:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=236)]
Right. And I think we can also remove barrier. I think barriers just after. Local.

##### **Flata** [[00:04:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=251)]
Okay.

##### **Chenyu** [[00:04:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=257)]
Anyway, I think that's it for CQ and we can move on.

##### **Chrism** [[00:04:24](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=264)]
Yeah. So. I looked into putting everything, putting everything into a. Docker. The smallest I got the Docker down to was three gigs, which seems a little bit big. So I didn't end up moving that.

##### **Chenyu** [[00:04:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=282)]
What are you those three gigs?

##### **Chrism** [[00:04:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=284)]
So a lot of it is the Intel OpenCL CPU runtime that we use. I looked into whether or not we can file to ourselves, but I think it's closed source. I don't know. It looks like they tried to open source it at one point and then. Gave up on it, I guess. So now it's. Still closed source. Is there a different runtime? I looked into it. So I looked into Rustical, which is Mesa's like you could use a Mesa OpenGL backend as your. As your C L runtime. But that's seg faults in the compiler. So it doesn't seem like a good. So there's also a portable OpenCL or POCL, but that one. Yeah. I think we used to use that. Yeah.

##### **Flata** [[00:05:29](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=329)]
Yeah.

##### **Chrism** [[00:05:29](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=329)]
I think it's a good thing. It seems to have issues as well. Like it doesn't support a lot of stuff or it claims to support. I think it's FB 16. It claims to support. But then when you actually try and do anything at FB 16, it crashes.

##### **Chenyu** [[00:05:40](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=340)]
Yeah. Wow. I didn't know this wasn't open source either.

##### **Chrism** [[00:05:49](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=349)]
Yeah. Yeah. Like when you Google it, there's actually a Pharonix article that says like, oh, they're open sourcing it. And then you click on the link and it's to a PR that has no history and didn't get merged. Yeah.

##### **Geohot** [[00:05:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=359)]
Yeah. I mean, says, yeah.

##### **Geohot** [[00:06:02](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=362)]
So then open.

##### **Chenyu** [[00:06:04](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=364)]
Yeah.

##### **Chrism** [[00:06:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=367)]
So I don't know that that the other thing is that we ended up installing LLVM like many different times. Like so obviously, co-manager has its own build at LLVM and then install LLVM as well. And then fortunately, I made it so that GPU ocelot no longer depends on LLVM. So we don't have another copy of LLVM there. Yeah. So I think that's also a big contributor to why the size is so big is just because we have like many different copies of LLVM lying around.

##### **Geohot** [[00:06:37](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=397)]
Should only be like 50 megs. LLVM is not that big.

##### **Chenyu** [[00:06:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=404)]
Yeah, I don't I don't know.

##### **Geohot** [[00:06:45](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=405)]
I mean, yeah, that's true. But I guess it all adds up.

##### **Chenyu** [[00:06:50](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=410)]
Yeah.

##### **Geohot** [[00:06:54](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=414)]
How bad is a 3G docker? How slow is that?

##### **Chrism** [[00:06:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=418)]
So I didn't try downloading it. I think it's pretty good. So there's also this kind of question of like, okay, so you how do you want to build the image? So what you could do is you could build it on master and then upload it to get a container registry or. And then every time like some PR runs, it downloads from master the Docker image. But that's a little bit frustrating because then it's like, okay, well, if you say we want to bump the LLVM version because we depend on some new feature from a Docker image. I didn't actually sell that information. I'd probably want the NF2019 LVM version. Then you need to have one PR that updates the LVM version. And then the next PR that actually, you know, depends on the change that you made totally fine with that.

##### **Geohot** [[00:07:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=462)]
But I think the bigger problem is just how long does it take to download through gigs through gigs is a lot.

##### **Chrism** [[00:07:48](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=468)]
Yeah, well, so fortunately, actually, you don't have to download three gigs. You only to download. 700 megabytes. So I should test it out. I should see how slow it is. Yeah, I don't know. I think. That's a little bit of a both a Florida.

##### **Geohot** [[00:07:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=479)]
I think we should just see how slow it is and see how long the... Because I want these CI jobs to be short, and I don't want to spend more than, say, 10 seconds setting it up.

##### **Chrism** [[00:08:10](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=490)]
Yeah, yeah. Yeah, when I was looking at this, there are definitely some that are slower, but on average, it seems like around 15 seconds. So that's why I hadn't done that yet, but I'll check and see how much faster it is to just download instead.

##### **Geohot** [[00:08:26](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=506)]
And then for the Intel thing, I know it downloads a ton of crap. Do we just need it all, or can we just delete files?

##### **Chrism** [[00:08:34](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=514)]
The problem is that we installed from Aft, because we can't just build it ourselves. I guess I could probably just pull out the binaries and see if we can just... That's what I'm saying. Is it like two SO files that we need? I'll have to check. My understanding is that it also installs the... compiler, and that's a separate thing. And then it also installs thread building blocks, which is like Intel's replacement for OpenMP. But I don't know. I will test that out and see if I can just pull out the SO files.

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=549)]
I bet it's two SO files.

##### **Geohot** [[00:09:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=551)]
Yeah.

##### **Flata** [[00:09:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=552)]
All right.

##### **Chenyu** [[00:09:15](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=555)]
Can you also comment on what are the slow jobs now, and what are the flaky ones?

##### **Chrism** [[00:09:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=562)]
Yeah, so some of the slowness, especially... especially in the install, like the setup TinyGrad step, is even though we're using UV, which did speed up some stuff, whenever we have to install the full testing, like TinyGrad brackets testing, that takes a while to install. And I think that's mostly in installing stuff like TensorFlow or installing Onyx. Those both do seem to be super slow to install.

##### **Geohot** [[00:09:50](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=590)]
Why do we still use TensorFlow? We use TensorFlow to test... I think we should just replace that with something else. Yeah. Or just not even test it, like should Keras... Yeah. Because it isn't worth installing TensorFlow over.

##### **Chrism** [[00:10:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=611)]
Yeah, yeah, that's probably true. And then the slowest stuff that's on Linux right now is OpenCL, which I think the runtime is just slow. Like whether it's the compilation or the runtime or whatever is slow. Something's just slow about that. Because I went through and I tried to get rid of a lot of the most egregious stuff, but it still takes two minutes and 30 seconds to run all the OpenCL tests

##### **Geohot** [[00:10:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=643)]
without there being one obvious thing that's like,

##### **Chrism** [[00:10:45](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=645)]
oh, this test takes a full minute to run or something like that. And then the macOS tests are just slow too. And I think what I need to do for that is I just need to say, like, okay, we're going to... We're going to put that near the same level of Windows support. The only issue there is that we really don't want to have the benchmarks where we run PyTests. Well, I mean, we don't want macOS to fail, but also we especially don't want PyTest on macOS to start failing because we didn't adequately test something.

##### **Geohot** [[00:11:13](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=673)]
So I don't think macOS is like Windows because I think testing metal is really important, right? So you basically have to run whatever your full backend tests are, no matter what. And it's all going to run in parallel. So it's not like it's going to be like slowed. Yeah, it's true. So, yeah, no, I mean, I think we just need to... There's not like a thing that we can do like what we did for Windows. I think we just have to like actually reduce the surface area that we feel, you know, that we have to test on the backend.

##### **Chrism** [[00:11:39](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=699)]
Yeah. Yeah, I mean, so the slowest macOS stuff right now is like the macOS unit and macOS metal models. I think those are the two slowest things. Yeah. But yeah, I mean, in theory, yeah, like, I guess WebGPU is actually different on macOS because it uses that metal backend. But in theory, any differences there are kind of down to the WebGPU runtime, not down to...

##### **Geohot** [[00:12:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=727)]
I would download all the logs and stick them in GPT and like just have a conversation about what the surface area actually needs to be. Like all the historical failures give you a lot of data points on this. Yeah, that's true.

##### **Flata** [[00:12:21](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=741)]
That's true.

##### **Geohot** [[00:12:23](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=743)]
Yeah, that's good. I should... I should put that into GPT. I hadn't done that.

##### **Chenyu** [[00:12:29](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=749)]
Why is this here?

##### **Chrism** [[00:12:31](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=751)]
Yeah, so I looked into that. That also... It's hard for me to tell because I can't reproduce it locally. I tried running that a couple of times on... Or more than a couple of times. I tried running that like... I ran it successfully 200 times like with the same parallelism constraints with the same runtime locally. And just never saw that failure. So I'm not entirely sure, but it looks like there's two failure modes. Both of them are some sort of segfault. And in one case, it segfaults in some like background thread that Python's not aware of. So the nice thing about... Like fault handler obviously prints all the threads, but it only prints threads that it's aware of that like are Python threads. And then if there's another thread that was spawned by... So for instance, we call it to the OpenCL runtime and then it spawns a thread. Then when that... If that spawned thread crashes, then we have no... We just know that it crashed. We don't know like anything about it.

##### **Geohot** [[00:13:28](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=808)]
Can you enable core dumps?

##### **Geohot** [[00:13:32](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=812)]
Yeah, I'll look at... Yeah, that should be possible.

##### **Chrism** [[00:13:39](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=819)]
And then there's also a different failure mode where it crashes in the compiler. And I have not explored... I'm not entirely sure. Like some of the most recent failures that we had in CI failures were because the compiler crashed.

##### **Geohot** [[00:13:51](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=831)]
Are we sure it's not out of memory? All right, like most of these things, are usually... Out of memory can manifest in so many different ways.

##### **Chrism** [[00:14:02](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=842)]
Yeah, I'm pretty sure it's not. Okay, I haven't checked all of these, but the last couple of times I checked these, when you look at the memory graph in namespace,

##### **Geohot** [[00:14:10](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=850)]
it doesn't show that it's out of memory.

##### **Wozeparrot** [[00:14:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=852)]
Hmm. And it might be...

##### **Geohot** [[00:14:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=857)]
Okay, so this one is running on GitHub runners.

##### **Chrism** [[00:14:20](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=860)]
So that's not... We don't know. We don't know if it ran out of memory, but it seems likely to me that it didn't run out of memory because the GitHub runners have more memory

##### **Geohot** [[00:14:33](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=873)]
than the namespace runners.

##### **Chenyu** [[00:14:37](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=877)]
Because I just had one failure in my latest PR, 16613, and 04 CL related saying fail at the same time. That's kind of weird, assuming it's running in good... Isolation. And it's like output values, value or not. I mean, one of the job crash, but every other thing, when it's like value mismatch, I don't really know what's happening. And of course, it finished.

##### **Chrism** [[00:15:08](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=908)]
Yeah. So I've seen that before, but I think it's just when... Once something in the runtime crashes, then the outputs are just completely unreliable.

##### **Wozeparrot** [[00:15:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=919)]
So this is like CI setup issue. So I think it's just like,

##### **Geohot** [[00:15:27](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=927)]
I don't know, I don't know. I mean, you could reinitialize the runtime every time for every runner,

##### **Wozeparrot** [[00:15:34](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=934)]
but that would just make it really slow.

##### **Geohot** [[00:15:39](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=939)]
Okay. I'm not sure that, like, I feel like the right thing is to figure out what the actual bug is here.

##### **Chenyu** [[00:15:50](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=950)]
Well, I mean, that makes sense.

##### **Geohot** [[00:15:51](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=951)]
If we can find,

##### **Chenyu** [[00:15:52](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=952)]
if we can root cause it properly, and fix it,

##### **Geohot** [[00:15:54](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=954)]
that would be nice. Yeah.

##### **Wozeparrot** [[00:15:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=958)]
Okay.

##### **Geohot** [[00:16:04](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=964)]
Yeah. I don't know if there's anything else. That's kind of it. I added,

##### **Chrism** [[00:16:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=971)]
or I split apart the comma tests, or the comma benchmark. And the DSP, since we barely run anything on comma fours right now, I moved... I moved the DSP benchmark to comma four.

##### **Geohot** [[00:16:28](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=988)]
Oh, I didn't realize they were different. We might want to look into Pockel, even if it doesn't support FP16. I don't know. I always hated that Intel thing anyway. And if it's causing trouble, you know my thoughts on Intel.

##### **Chrism** [[00:16:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1004)]
Yeah. Yeah. Yep. And I'll, I will, I will spend some time looking into, into Pockel and relooking into Rusticle as well. I think, I think Rusticle could be a good option because that seems much more modern.

##### **Geohot** [[00:16:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1016)]
Maybe, maybe it generates the wrong output if you're running it on an AMD CPU.

##### **Chrism** [[00:17:02](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1022)]
Yeah. When you Google this, this is what, this is what all of the Intel forums say. They're like, well, you're running on an AMD CPU. That's... No,

##### **Geohot** [[00:17:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1029)]
they're clowns. I mean, they're just, they're just such clowns as a company. I think, I don't know how developed Rusticle is. And it was always people who try it. If the only problem with Pockel is FP16, I think we just switched to that. I think it's also slow. I think, I think that's... Yeah. But there's also options for it. I bet it can be made fast.

##### **Geohot** [[00:17:32](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1052)]
I will. Yeah.

##### **Chrism** [[00:17:34](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1054)]
Yeah. Yeah. I'll look at that. And I'll also look at downloading that, that Docker image and seeing how bad it is. Yeah.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1062)]
But no, I mean, it really wouldn't surprise me if that wrong output is due to a bug in the Intel OpenCL compiler. If you have AVX2, but not AVX512 or whatever, whatever. Yeah.

##### **Wozeparrot** [[00:17:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1076)]
Yeah.

##### **Geohot** [[00:17:57](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1077)]
Yeah. Yeah. I'm not sure.

##### **Flata** [[00:18:03](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1083)]
Okay.

##### **Chenyu** [[00:18:06](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1086)]
Next, I put two Lama stuff together and we start with, as it was paired.

##### **Wozeparrot** [[00:18:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1097)]
So I merged MXFP8 to Jam. This helps DP convergence a bit,

##### **Chenyu** [[00:18:23](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1103)]
actually. DP convergence is consistently a bit faster.

##### **Wozeparrot** [[00:18:28](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1108)]
This doesn't really help MP convergence. There's something else that's bugged with MP that I'm still tracking down. That causes MP to not converge in the right amount of steps.

##### **Wozeparrot** [[00:18:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1123)]
Do you think it's a bug or numeric?

##### **Wozeparrot** [[00:18:49](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1129)]
It's really hard to tell if it's a bug or if it's numeric. There was a bug with this rand bug. So I hit the rand bug.

##### **Geohot** [[00:18:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1139)]
Where two of the weights were the exact same in it.

##### **Wozeparrot** [[00:19:05](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1145)]
Yeah.

##### **Wozeparrot** [[00:19:08](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1148)]
And I fixed that. I worked around that. And it doesn't seem to really change convergence. I don't really expect that to change convergence much. But it does make diffing between DP and MP easier.

##### **Wozeparrot** [[00:19:23](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1163)]
How many steps slower is it? MP is about 300 steps slower.

##### **Geohot** [[00:19:35](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1175)]
Do you have some lace in this?

##### **Flata** [[00:19:37](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1177)]
Yeah.

##### **Wozeparrot** [[00:19:39](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1179)]
This is AB.

##### **Geohot** [[00:19:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1182)]
This is AB, yeah.

##### **Wozeparrot** [[00:19:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1183)]
Of course, how many GPUs?

##### **Geohot** [[00:19:47](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1187)]
Can you start with two and see if that's better?

##### **Wozeparrot** [[00:19:51](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1191)]
Yeah. Because it can also be other issues.

##### **Geohot** [[00:19:55](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1195)]
Yeah.

##### **Chenyu** [[00:19:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1199)]
And I think previously, maybe you are already doing this, but just logging some stats to your gradients help previously.

##### **Wozeparrot** [[00:20:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1212)]
Yeah, I mean, I can pretty easily tell very early in the run if the run will converge just by looking at grad norm. Yeah.

##### **Chenyu** [[00:20:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1222)]
Yeah, at least they'll tune all right. And I think previously what helped me also was just log the max of gradients to help because if that goes really bad, you can see that.

##### **Wozeparrot** [[00:20:34](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1234)]
Yeah, that's probably the problem.

##### **Chenyu** [[00:20:37](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1237)]
And I think maybe just try two GPU to start with because all the overdues and things, and I would be really surprised if two performs very different from one.

##### **Flata** [[00:20:50](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1250)]
Yeah. Yeah.

##### **Wozeparrot** [[00:20:53](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1253)]
Yeah. Yeah. Yeah, Indian bug is really bad. I don't know.

##### **Wozeparrot** [[00:21:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1267)]
Just track down where it's diverging.

##### **Geohot** [[00:21:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1272)]
Do we use drop out?

##### **Geohot** [[00:21:14](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1274)]
Do we use batch norm?

##### **Wozeparrot** [[00:21:16](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1276)]
No drop out and no batch norm.

##### **Geohot** [[00:21:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1279)]
And that's usually the... Yeah. see differences, it's usually those two things.

##### **Geohot** [[00:21:30](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1290)]
But I don't know. The problem with all the tiny d types is numeric stability.

##### **Wozeparrot** [[00:21:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1296)]
Yeah, I mean, it's always something that you're called.

##### **Chenyu** [[00:21:39](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1299)]
Have you tried no op?

##### **Wozeparrot** [[00:21:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1302)]
I have not tried no op. Yeah, I don't know if that's going to.

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1312)]
So how close are we to getting 7db to train and work?

##### **Wozeparrot** [[00:21:57](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1317)]
It's unclear. I hope to have something by the end of this week, like at least kick off a 7db run again.

##### **Wozeparrot** [[00:22:06](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1326)]
So we've switched.

##### **Geohot** [[00:22:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1327)]
We're using MXFP8 on the?

##### **Wozeparrot** [[00:22:10](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1330)]
For MP, yes. Not for DP?

##### **Wozeparrot** [[00:22:15](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1335)]
Not for DP. It's slower. The kernel is slower.

##### **Wozeparrot** [[00:22:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1339)]
Well, I mean, that could be the difference.

##### **Wozeparrot** [[00:22:27](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1347)]
I've also done DP runs with MXFP8, and I'm comparing against that run.

##### **Wozeparrot** [[00:22:33](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1353)]
How much slower is it?

##### **Wozeparrot** [[00:22:40](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1360)]
There is a faster kernel I can pull. There's one other kernel that worked. This kernel, at least for MP, which was already pretty slow, this is about another like three seconds. I can pull. It's slower.

##### **Wozeparrot** [[00:23:00](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1380)]
That's crazy.

##### **Geohot** [[00:23:04](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1384)]
You're showing me like the 14 seconds should be like 11 seconds if we had the right kernel.

##### **Geohot** [[00:23:10](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1390)]
Where'd you get this kernel?

##### **Wozeparrot** [[00:23:13](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1393)]
Hipkin's just merged FPH stuff in like the past three months.

##### **Flata** [[00:23:20](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1400)]
It's been like a month. It's been like a month. It's been like a month. It's been like a month.

##### **Wozeparrot** [[00:23:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1402)]
Let's see.

##### **Geohot** [[00:23:24](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1404)]
What did the reference AMD 8B use?

##### **Wozeparrot** [[00:23:32](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1412)]
Reference 8B is DP .

##### **Geohot** [[00:23:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1416)]
I know it's DP, but did they use MXFP8, or did they use single?

##### **Wozeparrot** [[00:23:41](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1421)]
They used FP8, not MX.

##### **Geohot** [[00:23:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1424)]
OK.

##### **Wozeparrot** [[00:23:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1424)]
You don't really need MXFP8 at 8B scale.

##### **Wozeparrot** [[00:23:50](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1430)]
Yeah.

##### **Geohot** [[00:23:52](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1432)]
OK. But no, so there's no AMD run on the board that uses MXFP8.

##### **Wozeparrot** [[00:23:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1438)]
No. Because no one has really trained anything big enough on AMD yet to warrant. Yeah. Yeah.

##### **Wozeparrot** [[00:24:52](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1492)]
He went in, and done a thrillingrium run. I guess the sillyrium run was a lot slower than...

##### **Wozeparrot** [[00:24:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1496)]
You have a bad one? I don't know. I looked at that last minute. It looks the same to me.

##### **Wozeparrot** [[00:25:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1509)]
I generally can tell. The initial spike also isn't .

##### **Chenyu** [[00:25:13](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1513)]
This looks much bigger. Probably should change this graph to .

##### **Geohot** [[00:25:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1519)]
But they all have the same initial spike. I mean, I'm just looking at the log.

##### **Wozeparrot** [[00:25:24](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1524)]
Yeah, it spikes at different place. Which seems to matter a lot.

##### **Wozeparrot** [[00:25:30](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1530)]
It looks almost the same to me.

##### **Wozeparrot** [[00:25:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1536)]
It looks like a step late. Yeah, yeah.

##### **Geohot** [[00:25:41](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1541)]
One step is a. I mean, should we have this spike at all? This initial spike just seems bad, period.

##### **Wozeparrot** [[00:25:48](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1548)]
So on runs without the initial spike, it doesn't convert at all.

##### **Wozeparrot** [[00:25:57](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1557)]
It's very odd. I mean, I don't know.

##### **Geohot** [[00:26:08](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1568)]
This looks like . I can't obviously see what's wrong with the other one. What precision are you doing the all reduce in?

##### **Wozeparrot** [[00:26:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1579)]
We have 16.

##### **Wozeparrot** [[00:26:24](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1584)]
Is that OK? I've tried every . It doesn't seem to make a difference.

##### **Flata** [[00:26:34](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1594)]
Yeah.

##### **Wozeparrot** [[00:26:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1603)]
I think it was just like with a minor thing.

##### **Geohot** [[00:26:48](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1608)]
What happens if you just try for a 70 run?

##### **Wozeparrot** [[00:26:52](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1612)]
It'll just take a while, like a really long time. Yeah, I could . I mean, this whole run.

##### **Geohot** [[00:26:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1618)]
This whole thing is so slow.

##### **Wozeparrot** [[00:26:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1619)]
Why is it taking a day to do this?

##### **Wozeparrot** [[00:27:03](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1623)]
So it's six seconds for .

##### **Wozeparrot** [[00:27:08](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1628)]
Often it's just really slow on the CPU. And then because it's a bunch of steps on the GPU,

##### **Geohot** [[00:27:20](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1640)]
because you're creating and accumulating 32 times, like 32 times the kernel. So it's really slow.

##### **Flata** [[00:27:27](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1647)]
So it's a lot of work.

##### **Wozeparrot** [[00:27:28](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1648)]
Yeah. We've got to have a 70 soon. When is the deadline for 4.05? I don't know. October?

##### **Geohot** [[00:27:54](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1674)]
Are you sure? It's not sooner?

##### **Wozeparrot** [[00:27:57](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1677)]
It should be October.

##### **Flata** [[00:27:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1678)]
Yeah.

##### **Wozeparrot** [[00:27:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1679)]
Yeah. I just don't know if it's.

##### **Chenyu** [[00:28:01](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1681)]
I'll check and post. I'm not sure how late October is. I know it's before.

##### **Wozeparrot** [[00:28:08](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1688)]
So everything can be wrapped up before the holiday.

##### **Chenyu** [[00:28:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1697)]
OK.

##### **Wozeparrot** [[00:28:18](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1698)]
And then I'll .

##### **Chenyu** [[00:28:20](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1700)]
Try two GPUs, see if it shows anything. Yeah.

##### **Flata** [[00:28:26](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1706)]
OK.

##### **Wozeparrot** [[00:28:26](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1706)]
And then ML training 6.0 results should release today.

##### **Wozeparrot** [[00:28:34](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1714)]
Republic today. OK. Great. Oh.

##### **Chenyu** [[00:28:46](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1726)]
Which machine do you usually use to run these two?

##### **Wozeparrot** [[00:28:50](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1730)]
Does it only work for the MS350 or MS300?

##### **Wozeparrot** [[00:28:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1738)]
I'm normally on MD4.

##### **Geohot** [[00:29:01](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1741)]
Oh.

##### **Chenyu** [[00:29:03](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1743)]
Can you disable the password or something? I can only connect to 4. But I always saw you were training wrong. So I cannot test stuff.

##### **Geohot** [[00:29:15](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1755)]
I don't understand why you can't connect to 3. I can connect to 3 fine.

##### **Wozeparrot** [[00:29:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1759)]
Yeah. You have an account.

##### **Geohot** [[00:29:21](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1761)]
I don't know either.

##### **Flata** [[00:29:25](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1765)]
OK.

##### **Geohot** [[00:29:27](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1767)]
I'll look at that after.

##### **Wozeparrot** [[00:29:29](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1769)]
OK. And these won't work on the MS300?

##### **Wozeparrot** [[00:29:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1776)]
Not MXRP8.

##### **Geohot** [[00:29:38](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1778)]
And not the flash attention either.

##### **Wozeparrot** [[00:29:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1782)]
I see. OK. Yeah.

##### **Flata** [[00:29:51](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1791)]
OK.

##### **Wozeparrot** [[00:29:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1798)]
Let's move on. Next is the AMA schedule stuff. Can I hear you if you are trying to talk? Yeah.

##### **Flata** [[00:30:35](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1835)]
Okay. Chazal? Hello?

##### **Geohot** [[00:30:47](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1847)]
Hello, hello.

##### **Wozeparrot** [[00:30:49](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1849)]
Yeah, we can hear you.

##### **Qazalin** [[00:30:51](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1851)]
All right. I switch my network. So I've been working for a while. on getting llama to first match amd we are at two hours and 50 minutes last sprint we were at 11 000 kernels now we're at 9 000. no new uh custom kernels added just like i fixed rangeify to not make down copies we've got a few more to go and then we should match uh their speed i'm also mindful that you

##### **Geohot** [[00:31:23](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1883)]
have the july event so let me do a faster time yeah i think the july event would be a good time to to show that off if we could if we could beat that you know we could just really talk about how our how our uh tooling has gone from our ml perf submission down to uh you know something that beats theirs um so is that uh are those kernels uh generic the the removal of those of those two cat

##### **Qazalin** [[00:31:52](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1912)]
yep uh so far you can read all my commits they're like small scheduler books here and there

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1921)]
yes a few of them uh but cool and you think the the so how many is the is the md one

##### **Qazalin** [[00:32:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1929)]
amd has three thousand uh

##### **Geohot** [[00:32:15](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1935)]
yeah are we gonna we're gonna get that

##### **Qazalin** [[00:32:18](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1938)]
i'll take that the grain of salt though like their rccl kernel is a little weird it's a persistent kernel that just stays on the gpu uh but the main thing that we want to remove is so 2000 of the copy of the kernels that we have is just we're shrinking it can uh we're shrinking a tensor and then copying it and that's creating a contiguous instead of yeah like that's just that's just gonna go all right that's alone is gonna save twenty percent of the kernels total the kernels total we're gonna replace that with the kernel um in this case uh not extra kernels kernels total uh so fixing that should be beneficial to everyone

##### **Wozeparrot** [[00:33:05](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1985)]
great yeah just make sure we have we have small uh

##### **Geohot** [[00:33:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=1989)]
small regression tests for for each one of these things yeah i know that's a known bug where if you uh if you shrink things uh yeah it'll make a copy when in reality it should just be copying from the sub-buffer.

##### **Qazalin** [[00:33:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2002)]
Yeah. Also, I've been looking into removing contiguous from custom kernel. It's a pain. It's a pain that exists, and it's a pain to remove it. We should persist one of those.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2016)]
Yeah, yeah. It's one of those things that every time I try to spend 20 minutes on it, I realize it's harder than 20 minutes, but I think it's worth it. I mean, there should not be user-inserted contiguouses at the custom kernels. Those should be inserted after the scheduler resolves things.

##### **Qazalin** [[00:33:53](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2033)]
Right. It's very bad because since the contiguous exists, call right now copies stuff, and it's not because call is bad. It's because there was a substitute, and that substitute kept the contiguous around. I mean, you can't remove it.

##### **Geohot** [[00:34:13](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2053)]
That's effectively a user contiguous, which you can't remove. Yeah, I mean, this just needs to be fixed.

##### **Wozeparrot** [[00:34:20](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2060)]
Do you think you have a good way to fix it?

##### **Qazalin** [[00:34:25](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2065)]
I spent a couple hours on it last week. Gets annoying.

##### **Geohot** [[00:34:31](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2071)]
It's worth a couple days, yeah. It's got to be fixed. I know it's not easy.

##### **Qazalin** [[00:34:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2082)]
That's it. All I have, I have the full breakdown posted in the scheduler channel,

##### **Wozeparrot** [[00:34:47](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2087)]
so you can see exactly where we're spending kernel counts on.

##### **Geohot** [[00:34:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2096)]
Yeah. Cool.

##### **Geohot** [[00:35:00](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2100)]
Yeah, yeah, yeah. The copies, those would be great to get rid of. Yeah, I mean, the transposes, we just need to use the other gem kernel.

##### **Qazalin** [[00:35:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2111)]
AMD also has...

##### **Flata** [[00:35:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2117)]
Yeah. Yeah.

##### **Geohot** [[00:35:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2122)]
Yeah, but yeah, the whole point of this project also is to continually improve the tooling. I think it's a good grind. And the ultimate end goal, I mean, the thing in July is important, but the ultimate end goal is when we submit to MLPerf next, I want to have the best time for AP.

##### **Geohot** [[00:35:41](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2141)]
Yeah.

##### **Geohot** [[00:35:45](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2145)]
So, like, I don't think AMD is going to... Maybe they'll do a 4 or 5B on a huge number of machines. Who knows if that's comparable? But if we can just apples to apples beat them on AP, this is really good.

##### **Wozeparrot** [[00:36:00](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2160)]
Cool. Yeah.

##### **Geohot** [[00:36:01](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2161)]
So any other blockers, anything you don't know how to move forward with, or you feel like it's just more grinding?

##### **Qazalin** [[00:36:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2169)]
It's just a slog of scheduler bugs to fix. Yeah. Yeah. I tried a bit with GPT-515. It thrashes really badly. I wasted my weekend with GPT-515. It's very good at convincing you that I did the right thing. And when you look at the code, it's like...

##### **Geohot** [[00:36:28](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2188)]
Claude's even better at gaslighting you.

##### **Wozeparrot** [[00:36:32](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2192)]
Yeah.

##### **Geohot** [[00:36:34](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2194)]
Do you try Fable at all?

##### **Wozeparrot** [[00:36:40](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2200)]
Nope.

##### **Geohot** [[00:36:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2202)]
Yeah. Yeah. Yeah.

##### **Geohot** [[00:36:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2203)]
I think it's not that much better than GPT-515, if better at all.

##### **Qazalin** [[00:36:48](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2208)]
I mean, it's very good as... It was... I'm going to be clear with it. It was very good at finding the issues. Like, I can give it the list trace and it generates this. Like, it's good at processing things. Once it starts to write code, oh, God.

##### **Wozeparrot** [[00:37:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2227)]
Yeah.

##### **Qazalin** [[00:37:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2229)]
I basically hand wrote the gemfix that emerged today. Okay. And then I gave it the example. It's like, now continue with this. Now it's better. At least it doesn't run in circles. But yeah, I think, like, this search space of possible ways you can get the custom kernels wrong is very large. Like, you can just write very bad code.

##### **Wozeparrot** [[00:37:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2263)]
So it ends up creating things that mostly just NAND the model instead of fixing anything.

##### **Geohot** [[00:37:52](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2272)]
Yeah. Yeah. No, I think, yeah, we got to fix these fundamental scheduler bugs.

##### **Geohot** [[00:37:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2276)]
GPT definitely is not going to fix them.

##### **Flata** [[00:37:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2279)]
Okay.

##### **Wozeparrot** [[00:38:01](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2281)]
So we're working on that. Cool. Anything else?

##### **Geohot** [[00:38:13](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2293)]
Let's open. Next is my stuff.

##### **Wozeparrot** [[00:38:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2302)]
I think I'm one change away to remove cons unique.

##### **Chenyu** [[00:38:28](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2308)]
Still don't know too much about some of the qualify and function stuff. I have a PR that has all the tests. I think I can do it. I still don't know if it will break or not.

##### **Wozeparrot** [[00:38:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2323)]
Everyone test list.

##### **Geohot** [[00:38:48](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2328)]
Which PR? Do I need to look?

##### **Chenyu** [[00:38:51](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2331)]
So it's basically instead of looking into using embedded clone for anonymous buffer and not.

##### **Geohot** [[00:39:00](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2340)]
Yeah. That behavior is not really used. If it works, then it works. Like, whatever it is, it is.

##### **Chenyu** [[00:39:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2349)]
The issue is. I don't think. I think part of the reason custom kernel is noise. It's not very clearly spec. And because it's very flexible and the part of the different ways you can write custom kernels. I don't want to break Lama, but I'm also trying very hard to test this.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2376)]
Yeah.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2376)]
I mean, anonymous buffers just should be. I mean, that thing that you want should be a function and not a call. Like if it's going to. There should be no such thing as a call with anonymous buffers. This is why we have a distinction between function and call. An anonymous buffer effectively is something that's created inside of the function and the function can return that buffer.

##### **Chenyu** [[00:40:04](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2404)]
Yeah. So that's why my current change looks something like detect this pattern. If it's not a function, then it's not a function. If it's only returned by the function.

##### **Geohot** [[00:40:15](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2415)]
Yeah. Yeah. No, I'm going to see what you're doing here. I don't know. It's fine to get it merged. It's on me to make this spec cleaner. I have not. That spec is not is not correct yet. The function calls back is not correct.

##### **Chenyu** [[00:40:32](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2432)]
Yeah. So that's the part that. I'll find a way to test this on real Lama training. Then if. I think that's good. Probably merge this first. At least gets the full account sourced thing out. And I also do several small change. Oh, I remove the unsafe pet thingy.

##### **Geohot** [[00:40:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2456)]
Oh, add to path invalid.

##### **Wozeparrot** [[00:41:02](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2462)]
Wait. Oh, you switch pad to invalid. Oh, no, I switch pet to pad invalid. Yeah. The optimization step. Oh, okay.

##### **Geohot** [[00:41:20](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2480)]
I see the, the, the. Applian. The search thing.

##### **Chenyu** [[00:41:24](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2484)]
Yeah. Yes. So that is invalid now. So. As a result. I remove the unsafe pet thing.

##### **Wozeparrot** [[00:41:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2496)]
Great. Yeah. That's a, that's a minor thing.

##### **Chenyu** [[00:41:40](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2500)]
Yeah.

##### **Geohot** [[00:41:41](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2501)]
I mean, it's basically, yeah, we should just be able to switch all pads to invalid, right? Right now, if...

##### **Chenyu** [[00:41:47](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2507)]
There's a difference between this optimization action to the other thing. For optimization steps, you don't want to skip doing ALU on that invalid, because that's the point of doing the optimization, to pad to a multiple of four, for example, or pad to the size that you can do jam on. But the other pad to say the multi case, I think you really want to skip those invalid and not being part of the compute.

##### **Geohot** [[00:42:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2542)]
Yeah, but that's a different question, right? Like there's a question of like, there's a question of what you want the range to be, but you never actually want to do the ALU. You always want to gate the ALU.

##### **Geohot** [[00:42:42](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2562)]
What do you mean by that?

##### **Geohot** [[00:42:45](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2565)]
Well, you never actually want to do the ALU on the invalid, right? The thing about the pad to optimization action is you want the thing to be rounded to something. But the only reason you want it to be rounded to something is so you can do a further optimization action on that rounded thing. We can always remove... Yeah. ...all of the invalid ALUs.

##### **Chenyu** [[00:43:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2592)]
Yeah. So if you want to round something to a multiple of eight, then do a jam on it, then you need to rewrite that invalid to the actual number that jam would apply to.

##### **Geohot** [[00:43:27](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2607)]
Yeah, no, I mean, my point here is the distinction between these two things, it is the same thing, right? Like if I have something that I like, okay, the jam is 62 and I want to pad it to 64.

##### **Flata** [[00:43:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2616)]
Mm-hmm .

##### **Geohot** [[00:43:37](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2617)]
And then I pad it to 64. And then I do upcast eight, right? And now that divides evenly and I have eight and eight, right? Yes. The distinction in like the multi-case is I would pad that 62 to like 128 set, right? And if I pad it to 128 and then I upcast eight, I can upcast that eight and still pull the invalid out of the first one as well.

##### **Flata** [[00:44:03](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2643)]
Yeah. Okay. So that's the distinction. I'm going to do a

##### **Geohot** [[00:44:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2649)]
You see what I mean?

##### **Wozeparrot** [[00:44:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2651)]
I'm following.

##### **Chenyu** [[00:44:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2652)]
So for a jam case.

##### **Flata** [[00:44:14](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2654)]
Yeah.

##### **Chenyu** [[00:44:15](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2655)]
What I did was I replaced the invalid value to zero. So that loads zero flow into jam. And I think that's what you don't want to do for the multi-case.

##### **Wozeparrot** [[00:44:29](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2669)]
Well,

##### **Chenyu** [[00:44:30](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2670)]
You need a value that fit into the jam instruction. And that value needs to be zero. Yeah, yeah, yeah. But we should, okay.

##### **Geohot** [[00:44:39](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2679)]
The distinction between these things is if it's upcasted versus if it's globals. If it's upcasted, like, yeah, the thing actually is eight, right? Like the thing has a lane width of eight. You're not going to remove any of those eight. But if there's globals, there's a separate pass, which does like range clamping. Kind of like the thing that we do.

##### **Chenyu** [[00:45:00](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2700)]
Yeah. Let's let that understand. So my point is, all I did for the path to optimization is for the local case. I just replaced the invalid value to the identity with a reward. That's all I want. What I did. I didn't touch the global thing. So that won't fully work for your multi-case.

##### **Geohot** [[00:45:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2719)]
It won't fully work for the multi-case. Yeah. But yeah, we should still, we should change the semantics of pad. Like right now there is code in rangeify when it processes a pad that adds in aware. And that shouldn't be in rangeify. That should be in mixins. That should be in pad itself.

##### **Geohot** [[00:45:38](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2738)]
Yeah. So I think, I think that's the other things.

##### **Geohot** [[00:45:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2743)]
Oh, do you have more?

##### **Chenyu** [[00:45:45](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2745)]
Oh, I also fixed the comma in range. There was a body. Yeah. That gives you half of the step and he just happened to break. If that was half steps collide with each other. I saw that.

##### **Geohot** [[00:46:03](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2763)]
It's hard for me to read.

##### **Wozeparrot** [[00:46:06](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2766)]
Yeah.

##### **Flata** [[00:46:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2767)]
Yeah. Yeah. I was just trying to get the picture.

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2771)]
You mean the thing that does the, like if the there's two ends basically,

##### **Chenyu** [[00:46:19](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2779)]
Uh, is trying to use a range map to keep a state, but because each function has stayed not complete state. So if you, if you imagine if this three-wire is the other odor that every half step get complete first and there won't be issue. But here the issue is two half-step parts, then they're de-collides, then the state got corrupted.

##### **Geohot** [[00:46:53](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2813)]
Maybe this is actually better than I thought it was. And maybe this code that I was complaining about is old.

##### **Chenyu** [[00:46:59](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2819)]
Oh, I closed the bad one.

##### **Geohot** [[00:47:04](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2824)]
Yeah, I was just reading this. I'm rewriting the de-vectorizer, and I was reading this thing that deals with those. I don't know. I'll have to find it.

##### **Flata** [[00:47:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2837)]
OK.

##### **Geohot** [[00:47:18](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2838)]
But maybe this is not the problem. Yeah. Oh, merge reduce ends.

##### **Chenyu** [[00:47:26](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2846)]
I don't know what it is.

##### **Geohot** [[00:47:30](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2850)]
Yeah, it looks like you wrote it two months ago. There is code called merge reduce ends. Merge ends. It's in de-vectorizer. That's something else. That's not listfix.

##### **Chenyu** [[00:47:43](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2863)]
Listfix isn't written.

##### **Geohot** [[00:47:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2864)]
Yeah. Yeah, OK. Yeah, that merge reduce ends needs to be deleted. It's a bug that it ever happens, basically. Yeah, there was other issues with that.

##### **Chenyu** [[00:47:56](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2876)]
Yeah, and I think finally your get item comment.

##### **Wozeparrot** [[00:48:01](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2881)]
Yeah, I have probably like five things I can cling up.

##### **Chenyu** [[00:48:04](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2884)]
One's PTR D type. And VAC are gone. And I'll be happy to do loads.

##### **Geohot** [[00:48:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2892)]
So PTR D type and VAC are already effectively gone. So you can pretend that they're gone everywhere. And yeah, so I already have this for you. So this is already all correct. So for VAC, you can look at the shape. So the shape always matches VAC even

##### **Wozeparrot** [[00:48:30](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2910)]
in the current implementation.

##### **Flata** [[00:48:33](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2913)]
Oh.

##### **Wozeparrot** [[00:48:36](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2916)]
Oh.

##### **Geohot** [[00:48:37](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2917)]
So the PTR D type, so that it doesn't exactly work for the get item one. And I'm not exactly sure why. So there is no more PTR D type. You have an address space. There's four address spaces, global, local, reg, and ALU. Global, local, and reg are all effectively what PTR D type used to be.

##### **Flata** [[00:49:03](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2943)]
OK.

##### **Geohot** [[00:49:05](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=2945)]
Like they're all sort of pointer. They're all vectors. And I made a distinction between reg and ALU because C makes this distinction. When you do something like float A sub 4, like A bracket 4, that's basically memory. There's no guarantee that that's anything else. But yeah, I mean, if you can change that thing, if you can look at it. So you can also, the address space is now visible in Viz. It's in the upper right corner of each thing. Green is global. Yellow is local. Red is register. And gray is ALU. So yeah, so the get item cleanup. And then also, we have stack and vectorize. These should be unified into one thing. Yeah, it's kind of annoying. I mean, the whole get item thing should really become, like we should just not be afraid to just use index and shrink.

##### **Chenyu** [[00:50:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3007)]
So yeah, I think we can decide this later. It's very similar to why don't you just use range or when you want to write an A range and things like that.

##### **Wozeparrot** [[00:50:22](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3022)]
I don't think that's true.

##### **Geohot** [[00:50:27](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3027)]
The reason you don't use range when you want to write an A range is because that range is named.

##### **Chenyu** [[00:50:39](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3039)]
And this seems more like a different issue, right? It's like you have this ops that gives you a range already. Then why don't you try to use that? It's similar to index.

##### **Geohot** [[00:50:51](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3051)]
Well, but you should just be able to use index. And we should fix things so that you can just use index. You shouldn't be able to use range. Because range and A range are not the same thing.

##### **Wozeparrot** [[00:51:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3067)]
Why not?

##### **Geohot** [[00:51:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3069)]
Because the shape's different. If you have like A range 100, the output shape of that tensor is 100. If you have range 100, the output shape of that range is scalar.

##### **Wozeparrot** [[00:51:31](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3091)]
I don't know.

##### **Chenyu** [[00:51:33](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3093)]
But OK, this we can decide much later. Sure. Yeah, yeah. No, but we shouldn't be afraid to use it. We also have examples that use something like that to construct your tensor. Let's call range and pretend it's an A range.

##### **Geohot** [[00:51:50](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3110)]
There's ways you can do it. But yeah, I don't think they're the same thing. But my point is about the movement ops is index and stack should be first class movement ops, just like the others. We should be able to use them anywhere. We shouldn't be like, oh, you can't use this. You can't use index here. You can't use stack here. I made them the same color in viz for a reason. They should be like the same tier movement ops.

##### **Flata** [[00:52:16](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3136)]
Great.

##### **Chenyu** [[00:52:20](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3140)]
Sounds good. Let's quickly touch on your new style renderer. Sure.

##### **Geohot** [[00:52:26](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3146)]
Yeah, so it's finally done. All the renderers now take in the new style API. I hacked it quite a bit for x86. x86 still uses pointer D type and vec D type everywhere. But most of the rest of them are pretty clean. And it uses it internally. So the API from the output of code gen is no more pointer D type and no more vec. I think everything's pretty clean. The most notable new thing that's been added is you can use shrink inside of programs. And if you think about it, that's really what it is. If you want to do a load of a float for, well, it's a shrink. You apply a shrink to the buffer, which shrinks it to whatever your starting point is, like an index. But then you have a length, which is 4. And that's just the second argument to shrink. So I think that's pretty clean. It required a bit of changing to the way that pan shrink are specified. But I think that this new way to specify them now is, is very clean. And we no longer have to deal with things like, if it's end and begin, it's like, OK, well, now I've got to figure out, does end minus begin yield a constant after unsimplify on that? What if things are a little bit out of order? What if it can't simplify? So now it's just the offset, the shape, and that gives you that. The load, so that was the only thing that was really tricky. And that removes all of the casts. So we used to do cast. Cast used to be this overloaded thing. Yeah. Yeah, got to take away Shutting loss and all over. You could basically add result to this. So use of31R utilizar a. the expander to never use any of this vec to never do pointer cat all that stuff can be just deleted oh jepp is deleted from renderers um jepp is deleted from renders oh define local and define reg are deleted from renderers those are just buffer so there's two ways to get buffers uh in a program one is param and one is buffer uh param means it's bound to an external address and buffer means it's internal and i think that's pretty straightforward and there is like a real distinction between parameter buffer but buffer is basically like yeah it's an anonymous buffer and param is a name buffer um it's an anonymous buffer with scope of the function whereas param is is passed in from the outside so the scope is external um but yeah i think that's pretty clean now there's no more again no define local no defined reg in theory you could imagine a buffer that's defined global uh right the buffer address space can be global that's totally fine i agree we can decide if we're going to actually be able to do that in the renderer but it just means that that global is only scoped within that single function and it can't be accessed externally makes sense yeah so pretty happy with it it's slow but we have a real spec now we're working towards something we won't have to hopefully redo this again

##### **Wozeparrot** [[00:55:41](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3341)]
there's i look at this stuff there's no real way to make it cleaner and more we just need gpt 12. no it's like ideal like it says i think there's i think there's just not really a way i think

##### **Geohot** [[00:55:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3358)]
there's just like i've read all the different irs now lvmir and ir and like i think that a lot of the annoying things in those irs don't exist in uops and there's like there's like there's nothing to

##### **Wozeparrot** [[00:56:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3372)]
take away anymore

##### **Geohot** [[00:56:17](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3377)]
um yeah versus you know the g type thing needed to go but yeah well okay there's still a few like there's still a few cleanup things like barrier needs to go but uh uh yeah

##### **Chenyu** [[00:56:31](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3391)]
when i still had fable i i have it to read a whole code base and read a whole spec and map all the things that doesn't uh look the same i have a big list of things that i can't read and i can't read

##### **Geohot** [[00:56:45](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3405)]
so things to address nice yeah fable was uh fable did did after i did the first two ports so i did the c style one the lvm one fable managed to do the rest of them pretty nicely except for x86

##### **Wozeparrot** [[00:57:02](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3422)]
so hope we get it back soon uh almost all the time uh what are you going to do or something

##### **Flata** [[00:57:16](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3436)]
uh no uh not a whole lot just added those benchmarks and the um uh and the and the fake data so i can just quickly test the timing i think we're just uh definitely over 24 hours i think like 33 hours but that's without beam so i think that's my next step just taking a look into that and then fixing the tiny jit issue on the evo step sounds good yeah uh i think once we have this trend

##### **Chenyu** [[00:57:44](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3464)]
we should look into it like why am is not working it's like correct maybe after hdq2 we will know better okay

##### **Chrism** [[00:57:54](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3474)]
okay uh is comma happy i see another jit yes uh so i have a pr open i guess open pilot to get them uh to the latest tiny grad um had some like a range that was using device equals okay uh so that wasn't it just like a flick merge but it's uh i have a review so it'd be kinda cool if that was using anchovies a little bit i haven't searched it in super close detail but i i think it has something to do on the emulating the type uh emulating float 16 support because we round g normal is to zero

##### **Chenyu** [[00:58:38](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3518)]
um yes is that do you know if that issue is like a bug or it's just block numerical being slightly different?

##### **Chrism** [[00:58:48](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3528)]
It looks like it's just a numerical difference thing, like basically when you do the rounding.

##### **Wozeparrot** [[00:58:55](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3535)]
Can you look into that?

##### **Chrism** [[00:58:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3538)]
Yeah. Yeah, I don't know. I'll talk to them and see. Apparently, this is not a blocker for them, but it's just an .

##### **Chenyu** [[00:59:09](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3549)]
You don't need to spend a lot of time on it, but I think it's a good idea to have a response to that. Yeah. Yeah. I'll . We just need to say if we are going to do anything or we are not going to do that, and you can deal with it.

##### **Chrism** [[00:59:24](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3564)]
Yeah, for sure. No, I haven't. I literally spent maybe a minute looking at it, so I don't know.

##### **Geohot** [[00:59:31](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3571)]
I'm not entirely sure, but I will take a look a little bit more and see what's up.

##### **Wozeparrot** [[00:59:38](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3578)]
Yep.

##### **Chenyu** [[00:59:40](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3580)]
We got a lot of . First time contributor just putting things in Cloud. That's slightly annoying. Please don't do that. But I think those people are probably not in this meeting, so here's that.

##### **Wozeparrot** [[00:59:58](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3598)]
OK. Anything else? Do we cover everything? Any closing words?

##### **Geohot** [[01:00:07](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3607)]
Wait, we can probably, well, I'll ask Harold if he can close the, OK. OK.

##### **Chrism** [[01:00:12](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3612)]
If he can close the issue that he has open that we think is fixed.

##### **Chenyu** [[01:00:16](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3616)]
OK. Oh, and we probably should also update the model to include their new release one.

##### **Chrism** [[01:00:24](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3624)]
They actually don't. There's no, there's a new DM model on 0.11.1, but there's no new model on, like there's no new driver model.

##### **Chenyu** [[01:00:33](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3633)]
Yeah, I mean, you just need to pin to whatever they release. It doesn't need to be a different model.

##### **Geohot** [[01:00:40](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3640)]
Sure. Yeah, yeah. I'm going to try to do that. I see what you mean. Yeah, OK.

##### **Chenyu** [[01:00:45](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3645)]
Anything else, George?

##### **Geohot** [[01:00:49](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3649)]
That's pretty much it. I think things are going. I think this will be the summer of spec tightening. And then when the summer's over, we'll have a very solid foundation where everything has a clear reason.

##### **Chenyu** [[01:01:04](https://www.youtube.com/watch?v=t4-yUBzsr-I&t=3664)]
Great. OK. That's it for this meeting. Thank you, everyone. See you next week. Bye bye. Bye.
