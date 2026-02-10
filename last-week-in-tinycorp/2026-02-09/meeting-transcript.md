# 2026-02-09 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- compiler renderer
- llama training flash attention
- drivers
- assign setitem
- assembly
- viz / fast gemm
- other issues and bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=4xD6QrFdvYc)

### Highlights

- **[Company Update](#geohot-000007)**: Tinygrad now has a Hong Kong office in progress—Geohot signed an offer-to-lease using the company “CHOP” stamp and expects the building/lease to proceed.
- **[Sales & Fulfillment](#geohot-000105)**: Sales look okay, but they’re behind on filling orders; PNY was slow shipping the BlackBell GPUs, though they may have arrived now.
- **[Compiler: Float Decompositions](#chrism-000130)**: Float/dtype decomposition is working—FP8 can be emulated (defaulting to FP16) via a lattice of supported types; BF16/FP16 are explicitly tested so far.
- **[OpenCL Compile Caching Plan](#geohot-000420)**: For OpenCL, keep the compiler class and disk cache behavior—compile from the CL program while still caching properly, and avoid caching any “fake/no-op” compiler output.
- **[Sprint Goal Pressure: image==1](#geohot-000600)**: Geohot calls out repeated sprint goals and warns about “rabbit holes,” stressing that resolving `image==1` is blocking a lot of other work.
- **[Metal Compiler: Commit to Fast Path](#geohot-001003)**: For Metal, Geohot wants to delete the slow compile path and ensure the fast XPC-service compiler path stays working (and is properly tested).
- **[Llama Training MFU Improvement](#wozeparrot-001240)**: Llama training MFU is up ~2× week-over-week to about ~8%; they’re focusing on profiling/flash-attention kernels to keep improving.
- **[Periodic Step Slowdown Debugging](#geohot-001750)**: Investigating an AMD issue where every ~300 steps one step becomes extremely slow; suspects ring-buffer/overflow edge conditions and suggests forcing the bug to reproduce more often by making ring buffers very small (via an env var).
- **[Assign/SetItem & JIT Semantics](#chenyu-003542)**: Slice-assign semantics should match eager (“as if you realized every line”), but JIT isn’t capturing slice-assign correctly without explicit realizes; exploring designs to track these dependencies cleanly.
- **[Refactor: Universal `call` and Schedule Cleanup](#geohot-003746)**: `kernel`/`custom_kernel` ops are removed in favor of universal `call` (tensor-level, uops-level, or fully custom program); next goals include param-based schedule cache, multi-level call tests, and removing `schedule_item`.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=0)]
So let's start with company update. We have a Hong Kong office now.

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=7)]
I signed a... Well, I didn't sign a lease yet. I signed an offer to lease, and I used our company CHOP, which I learned about. A company CHOP is an official stamp, and I had to walk to Admiralty to get it. It was in our secretary's office. An official stamp that says Tinygrad Corp HK. So I stamped that on the offer to lease, and now we hopefully have a building.

##### **Geohot** [[00:00:38](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=38)]
Great. Well, anything else? That's it. Our sales going. Seems fine.

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=65)]
Yeah, seems okay. Maybe sold another one. We're a bit behind on getting orders filled. PNY was slow to ship us the BlackBell GPUs, but I think we got them now.

##### **Geohot** [[00:01:20](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=80)]
Great. Okay. Okay.

##### **Chenyu** [[00:01:25](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=85)]
Next is the compiler. So renderer, refactorer and stuff?

##### **Chrism** [[00:01:30](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=90)]
Yep. Yeah. So, I mean, the big thing for last week that I worked on was getting float decompositions working, which that's all set up now. So that's FP8s can be emulated into... By default, they're emulated to FP16, but it just uses the lattice. So that's a little bit of a challenge to figure out which... Like, it goes through each option of the lattice until it figures out what the correct thing to use is based on what you have supported. Same thing with BFloat16 and FP16. Yeah, those are the only types that are explicitly tested right now. I mean, in theory, it should work for other types as well, but we don't test them. So...

##### **Geohot** [[00:02:29](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=149)]
I'm a little worried. I mean, these two goals, removing compiler pair and image equal one, were also your goals on the previous sprint.

##### **Chrism** [[00:02:37](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=157)]
Yeah.

##### **Geohot** [[00:02:38](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=158)]
This has to... I mean, we need to see progress here. Yeah. Like, I don't know if we need every D type composition to work, but as far as I know, the compiler pair class is still present in the thing and not everything's going through the new path. And I don't think we've gotten to the challenge yet, which is what are you going to do for OpenCL?

##### **Chrism** [[00:02:56](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=176)]
Yeah. Yeah. No. I have a PR open, which is... It's passing all the tests for removing compiler pair. Compiler pair is completely gone. But yeah, that's another thing I should ask about, is what to do about OpenCL. So right now, I just replaced the compiler with the default dot encode compiler. And so then what you do is you run the same compiler pass. You do it in a CL program. Instead, I mean, the problem with this is that there's no disk cache, which is why I haven't merged it.

##### **Geohot** [[00:03:37](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=217)]
Why is there no disk cache?

##### **Chrism** [[00:03:40](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=220)]
Why should that affect the disk cache?

##### **Geohot** [[00:03:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=222)]
There's no disk cache of the compilation. What else is cached on the disk? Yeah. The source code is cached. Where is the source code cached?

##### **Chrism** [[00:04:04](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=244)]
Because the compiler is like the capital C compiler should cache it, right? Or I guess no, because I didn't set a cache key. So I guess it's not. Right now, it's not. But that could be cached there.

##### **Geohot** [[00:04:20](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=260)]
Yeah. So why can't you just use the disk cache but call OpenCL program?

##### **Chrism** [[00:04:26](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=266)]
Oh, yeah, you can. I just haven't done it yet.

##### **Geohot** [[00:04:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=271)]
Yeah, OK. But so it should call CL compile from CL program, and it should still get the disk cache. Yeah, yeah.

##### **Chrism** [[00:04:37](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=277)]
I mean, the problem is that, yeah, yeah, no, that'll work. Yeah.

##### **Geohot** [[00:04:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=281)]
And it definitely shouldn't cache the fake no op compiler that just doesn't code.

##### **Geohot** [[00:04:47](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=287)]
Yeah. Yeah. Yeah. Yeah. No, that, that, that, that, that.

##### **Geohot** [[00:04:55](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=295)]
Yeah, that seems OK. Yeah. That seems OK. And that seems like an OK way to deal with compilers that need a device.

##### **Chrism** [[00:05:07](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=307)]
Yeah. Yeah. I guess then you keep the compiler class around. And I just turned it into a function. But if you want to have that caching behavior, you might as well just keep the compiler class around. Yeah, that makes sense.

##### **Geohot** [[00:05:22](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=322)]
Wait.

##### **Geohot** [[00:05:24](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=324)]
You still have the cache for the other ones, right?

##### **Geohot** [[00:05:27](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=327)]
Yeah. How does that work if that's a function?

##### **Chrism** [[00:05:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=331)]
Oh, no, I just made it a function for CL compile.

##### **Geohot** [[00:05:36](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=336)]
Oh, yeah, I don't think that's right. I think it should just be the same class. Just use it in a different place. Yeah, that makes sense.

##### **Chrism** [[00:05:45](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=345)]
Cool.

##### **Geohot** [[00:05:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=346)]
Yeah. And make sure all the stuff's tested. And I don't think we have a lot of testing around whether things are properly being cached or not.

##### **Chrism** [[00:05:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=352)]
Yeah. Yeah.

##### **Geohot** [[00:05:55](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=355)]
Oh, oh, oh. Yeah.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=356)]
I'm just trying to figure out how we can test that.

##### **Geohot** [[00:06:00](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=360)]
Yeah, no, again, I get really concerned when I see sprints that have the exact same goal and there's not really progress toward it, right? Because what you can have is, I'm not even sure exactly why we had to decompose floats. I understand why we had to do longs. But you can get this infinite rabbit hole where you're always adding new tasks. And if you're not popping back off the stack, it's really important to get these things resolved. And we really need image equals one resolved. Yeah. Because a lot of stuff is blocked. A lot of stuff is blocked on that.

##### **Chrism** [[00:06:29](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=389)]
Yeah. Yeah. Not... Yeah. Yeah, you're right. Yeah, that ended up being much bigger of a rabbit hole than I realized. That really was, at the end of the day, there was not a good reason to be... It was not related to the removing compiler errors, as much as I realized. It was much more about refactoring, is DTIP supported than anything else?

##### **Geohot** [[00:06:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=412)]
Yeah. I mean, yeah, we can't have... This is why we have sprint goals. We can't have things just going on the stack like that. Yeah.

##### **Chrism** [[00:07:00](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=420)]
Yeah. Yeah.

##### **Geohot** [[00:07:02](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=422)]
For sure. Can you also comment on the LLVM single stuff?

##### **Chenyu** [[00:07:12](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=432)]
Yeah.

##### **Chrism** [[00:07:13](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=433)]
I tried. That doesn't happen on my laptop. But I will try and see if I can reproduce it maybe in benchmarks or something. It's weird, because I have seen issues like that in the past where something gets loaded. But I ran the one line repo that was in...

##### **Chenyu** [[00:07:34](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=454)]
I think that certainly is not deterministic, right? I don't know if you run the test or run the repo that's from cloud, or I can run something. I can give you more comment to try later. But...

##### **Chrism** [[00:07:47](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=467)]
Yeah, I tried both.

##### **Chenyu** [[00:07:48](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=468)]
Because we're on the test with minus an auto... Who knows? Who knows how many cores you have and things like that.

##### **Chrism** [[00:07:57](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=477)]
Yeah.

##### **Chenyu** [[00:07:57](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=477)]
Yeah. Yeah. I will... Because the arrow seems to be the loading LLVM symbol and the metal symbol complex or something. I don't know why it segboats. It shouldn't. But that's what happened. And that's kind of annoying.

##### **Chrism** [[00:08:12](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=492)]
Yeah. I mean, for sure it's annoying. Yeah. I mean, the problem is that I think when you load a library that depends on LLVM, the dynamic length doesn't... So, I mean... ...filer properly. Yeah.

##### **Chenyu** [[00:08:24](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=504)]
It's fine if my system loads things in a weird way or not in an intended way, but we shouldn't let it crash, right? If we know this is the case, we should at least catch and report properly. Yeah. No.

##### **Chrism** [[00:08:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=521)]
I believe there's other people who probably have a system that's similar to yours. So, this is probably breaking for other people.

##### **Chenyu** [[00:08:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=526)]
I am not using a special system. Yeah. Exactly. Yeah.

##### **Chrism** [[00:08:50](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=530)]
Okay. So, yeah. So, that's weird. I'll look into that. That's definitely odd. Yeah. I don't know off the top of my head. Also, the thing that Claude said that was interesting was that... Which I didn't realize this either, but was that Metal compiler was never being used with the olds.

##### **Chenyu** [[00:09:13](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=553)]
Yeah. And that's why if you run the Python-M device on Metal, it always suggests a weird... I think it's called the empty compiler. And I think that's just part of the weird thing that was introduced initially for the compiler-renderer pair. So, there's that.

##### **Chrism** [[00:09:30](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=570)]
Yeah. Actually, I do want to ask about that. That weird Metal... There's two compilers for Metal, and one of them basically does the CL thing where it compiles in the Metal program. And one of them does...

##### **Chenyu** [[00:09:44](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=584)]
I think that was because there was some issue when you tried to use the CL thing. So, the Metal compiler has other proper compiler it complains or something. So, there was a change that made similar to CL that you just late render your stuff or late compile your stuff.

##### **Geohot** [[00:10:03](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=603)]
Yeah. So, I don't want to do that for Metal. I don't really care about CL because no one really uses CL. But for Metal, we have to make sure the fast compiler works. So, the fast compiler... The way that the Metal compiler works is that there's a service. Yeah. And it makes an XPC call to the service to do the compilation, and we have to make sure that stays working. The main reason we added that was to make Metal work... Do the compilation in Beam, so it didn't have to do the compilation in the single process. But we should really delete the slow path, and we should just make 100% sure that the fast path works. Yeah.

##### **Geohot** [[00:10:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=641)]
Well, the interesting thing that...

##### **Chenyu** [[00:10:43](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=643)]
I think we know there's a real test benchmark we should use that. Yeah. Like, reasonably, to catch things like this.

##### **Chrism** [[00:10:54](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=654)]
Yeah. Yeah. Well, anyway, the thing that Claude had been pointing out was that it's not... Before this change, it wasn't using the fast path, the fast compiler.

##### **Geohot** [[00:11:06](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=666)]
Yeah. Yeah. I totally believe that. That's probably something we didn't test that well.

##### **Chenyu** [[00:11:13](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=673)]
Yeah. So, I mean, just keep this in mind when you do the cleanup.

##### **Chrism** [[00:11:18](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=678)]
Yeah.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=679)]
Yeah. But, yeah, what I would like to do is just delete the slow path entirely and make sure that the fast path works.

##### **Chrism** [[00:11:28](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=688)]
Yeah. The thing I was wondering is maybe there's a version of Mac OS or something that doesn't have this API, or maybe that was the reason it was added. But I guess if it's just...

##### **Chenyu** [[00:11:38](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=698)]
It started with the slow path, I think, then the fast path was a service that was added after. And the old one was not deleted. I believe that's the case. Just use Claude to relook at history analytics. Yeah. Yeah.

##### **Chrism** [[00:11:53](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=713)]
No, I'd love to look at that in a little bit. But, yeah, I just want... Especially considering that this thing is segfaulting on your laptop, but it's not segfaulting on my laptop, I want to make sure that my laptop isn't weird and...

##### **Geohot** [[00:12:05](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=725)]
Yeah, that's fair.

##### **Chenyu** [[00:12:10](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=730)]
I mean, those tests run in separation or single core doesn't sometimes sense fine. So... They are certainly not slap deterministic. It's just...

##### **Geohot** [[00:12:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=741)]
Yeah. Yeah.

##### **Chenyu** [[00:12:23](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=743)]
Sometimes...

##### **Geohot** [[00:12:24](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=744)]
I'll keep that in mind for this change. Okay. Sounds good. Okay. Next, we have Lama training. Flash attention.

##### **Wozeparrot** [[00:12:40](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=760)]
Yeah. I think we're up 2x on MFU over last week. So we're at about 8%. Yeah. Yeah. Its in the cleaned quality mode. The mouse handretto is actually retgets to 9% by currently compared to testing orieu in Involvedivamente Podcast. And now we have exits related to testing. So there are 10 sú Rule, 14 at damage and 16 at evaluation. I suspect this one's not the default value. Is there any platforms that, well, actually we have results about time? Yeah. and seeing if that's faster.

##### **Geohot** [[00:13:20](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=800)]
So, I know the proper Hip Kittens one. I know their gem doesn't actually work. They didn't test it very well. There's race conditions in it.

##### **Wozeparrot** [[00:13:28](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=808)]
Supposedly, their Flash Attention one has a Llama training example.

##### **Geohot** [[00:13:36](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=816)]
Yeah, I'll believe if they actually trained any Llama. The one I'm more interested in is the one that was actually used in ML Park.

##### **Wozeparrot** [[00:13:44](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=824)]
Yeah, I think that's the Ider one.

##### **Geohot** [[00:13:47](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=827)]
I can look into that too. Yeah, I wonder if we can grab that. What do I update? 4.2% MFU

##### **Chenyu** [[00:14:01](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=841)]
to 8%?

##### **Geohot** [[00:14:03](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=843)]
Yeah, we'll do that.

##### **Chenyu** [[00:14:09](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=849)]
I was thinking about this yesterday. So, you know, our latest run is 22 hours. Yeah, 22 hours. So, that's about 10x dip from the ML Park. And we know they're supposed to train with FP8, something like that. So, that's probably 2x.

##### **Geohot** [[00:14:27](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=867)]
They definitely train with 5x. Yes. I think they're stepping 500 milliseconds for a BS16 step. Wait, our step's only like 2 seconds. For a BS8 step.

##### **Wozeparrot** [[00:14:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=886)]
So, we need about 2x their steps to complete.

##### **Geohot** [[00:14:51](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=891)]
Oh, I see. We're not running BS16 because we can't fit memory. But if we can fix the memory, we can run BS16. Yes.

##### **Geohot** [[00:15:01](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=901)]
I think that'll get us a good bit of MFU. Why would that be slower? No. Is flash attention?

##### **Chenyu** [[00:15:13](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=913)]
Faster if you have bigger tensor?

##### **Geohot** [[00:15:16](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=916)]
Something like that? No, it's not about that. It's about RAM. Oh, so we are

##### **Geohot** [[00:15:24](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=924)]
waste from RAM, is what you're saying? Well, if you do grad accumulation, the flops are the same, but the RAM bandwidth

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=934)]
doubles. Yeah, but is that a bottleneck? So, it's bottlenecked by flops.

##### **Geohot** [[00:15:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=946)]
Gem might be bottlenecked by flops, but everything else is probably bottlenecked by RAM now.

##### **Geohot** [[00:15:51](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=951)]
Interesting.

##### **Chrism** [[00:15:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=952)]
Okay.

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=955)]
Or at least our ability to access the RAM anyway.

##### **Geohot** [[00:16:00](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=960)]
But yeah, we've got to improve that profiler script a bit. Make sure to exclude eval. I don't know why it says custom forward is slower, but yeah. I think looking at other flash dungeon kernels. And...

##### **Wozeparrot** [[00:16:14](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=974)]
Is it just that? And then I'm still seeing this weird issue where every, like, 300 or so steps, there's one step that takes extremely long.

##### **Geohot** [[00:16:27](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=987)]
I posted about this before. In AMD hardware. It seems like one of those, like, 4 billion overflow kind of things.

##### **Wozeparrot** [[00:16:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1001)]
Yeah, and the weird thing is the amount of time this extremely long step takes increases over time. So near the end of training, the step is taking like five minutes to complete.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1014)]
Which seems very wrong. Yeah, this definitely sounds like some driver thing. No more general ideas? Actually, no. I'll take a look.

##### **Nimlgen** [[00:17:20](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1040)]
I think so. For my profile to just stuck in this admit function. I think it's just a little bit of a

##### **Chrism** [[00:17:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1051)]
OK.

##### **Nimlgen** [[00:17:32](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1052)]
Yeah, I'll take a look. Maybe it's something about Ring buffers that I'm not sure is what it sounds like, especially

##### **Geohot** [[00:17:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1061)]
if it's like determinedistically a number of steps.

##### **Geohot** [[00:17:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1066)]
I'm going to buffer overflows.

##### **Geohot** [[00:17:50](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1070)]
In general, the way I like to debug my Green buffer edge conditions is to add an environment variable that make ring buffers very. very tiny and then see what happens. I think the way to debug this kind of thing is first to try to get it to happen more often with whatever

##### **Geohot** [[00:18:11](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1091)]
it might be. Yeah. Cool, yeah.

##### **Geohot** [[00:18:25](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1105)]
Overall, I'm pretty happy with progress. If we can continue to get these kind of MFU improvements week over week, hopefully we get it up like 20% this week. And then next week, we can start thinking about actual 405b.

##### **Wozeparrot** [[00:18:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1121)]
Yep. There's some other stuff to hit before 405. I'm not entirely sure if model parallel works currently.

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1130)]
Oh, yeah. We should try that with 8. Yeah. There's some stuff to test before then.

##### **Chrism** [[00:18:56](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1136)]
Cool.

##### **Geohot** [[00:18:58](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1138)]
Hopefully, I don't think the refactor broke anything. I tested it. We no longer have custom kernel. Custom kernel is now call. And hopefully, that syntax makes sense. You can just basically call a kernel. You can put a kernel in, be that a kernel with a sink like Tiny Kittens does or a kernel with a kernel. But it's not a kernel.

##### **Geohot** [[00:19:25](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1165)]
It's a kernel UOP, like the Asm.gem does. Anything else for Lama training? That's all. OK. Next, we have drivers. Yeah. So this week, I've been fixing different issues.

##### **Nimlgen** [[00:20:04](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1204)]
So yeah, in AMP account, QCOM also was fixed. Also, we now have, like for the EMD GP driver, we should have fast exit, so not waiting for the whole timeout. I'm still experimenting with. I'm still experimenting with the I can definitely do a lot of stuff on my system, which

##### **Geohot** [[00:20:50](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1250)]
brings down the entire system. So I'm using these. I'm using AMD GPU kernel driver. Yeah. It's really annoying on my laptop when it brings down the whole display, and then I got a reboot.

##### **Geohot** [[00:21:05](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1265)]
I wonder if there's anything we can do. Yeah. I don't know. It might not be any better about this.

##### **Nimlgen** [[00:21:20](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1280)]
Yeah, I'll take a look. But currently, I've just. I've made heap running on the tests, like the GPU crash ones. And it just, after the first failure, it just for other calls, it just returns an error. So it's like a bad state in heap either. I don't know. Maybe our backend doesn't support something. Yeah, I'll take a look into that. I mean, a bad state? But for memory files. Yeah.

##### **Chrism** [[00:21:53](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1313)]
Yeah.

##### **Nimlgen** [[00:21:53](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1313)]
Yeah.

##### **Geohot** [[00:21:54](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1314)]
A bad state in heap is fine if we can't save the process. But does it crash the display on the GPUs? It's one of the things I want to test with the Newstrix Halo computers.

##### **Nimlgen** [[00:22:07](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1327)]
Probably crashes when it just resets the GPU or something like that.

##### **Geohot** [[00:22:14](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1334)]
What I've noticed is that my computer will stay up as long as the Python process keeps running. But as soon as I kill the Python process, I'm going to fail. But as soon as I kill the Python process,

##### **Geohot** [[00:22:23](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1343)]
it then brings the computer down. Yeah, I see.

##### **Nimlgen** [[00:22:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1351)]
I don't know if you can grab the mask and share this. I don't know. Maybe something in the logs the MDGPU tries to do.

##### **Geohot** [[00:22:40](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1360)]
Yeah, we should be able to reproduce this now

##### **Geohot** [[00:22:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1362)]
on the Halo machines. Actually, yeah, I can try to do that.

##### **Nimlgen** [[00:22:53](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1373)]
But I've never seen it crashing, like, rebooting the whole system.

##### **Geohot** [[00:22:59](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1379)]
It doesn't reboot the whole system. It just brings down the display driver in a way that it doesn't recover. So it brings down my monitor. And it's a laptop, so I don't really have a choice but to reboot. But fun fact, Metal, if you run a long-running Metal kernel and kill the process, not only does the kernel not die, it seems to run forever. Yeah. And then your laptop appears normal and usable, your Mac, except that when you run AnyTop, it draws 40 watts. And I asked the MLX guy about this, and he's like, oh, you just have to reboot. I'm like, what?

##### **Nimlgen** [[00:23:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1421)]
Yeah, I've experienced exactly the same, yeah.

##### **Geohot** [[00:23:43](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1423)]
It's crazy. It's crazy that Apple doesn't have real process isolation on their GPU.

##### **Geohot** [[00:23:53](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1433)]
Yeah, and the MLX guy is like, nope, nope, we don't have any way to reset the GPU. So yeah, if we get this working, we're doing better than Apple. Any progress on NVIDIA profiling without the driver?

##### **Nimlgen** [[00:24:15](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1455)]
No, no major progress. So yeah, this week I'll dig into the issue with, like,

##### **Geohot** [[00:24:22](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1462)]
LAMA and focus on DNV. I see on this call.

##### **Chenyu** [[00:24:34](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1474)]
Do you have any issues that you want to bring up here?

##### **Harold** [[00:24:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1482)]
No, no, we just merged the Calibration and removed OpenCL from OpenPilot. And so far, that seems good, so making some progress.

##### **Geohot** [[00:24:54](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1494)]
Nice. And yeah, if you want us to make sure the speed doesn't regress on that, just make sure we have it in our benchmark.

##### **Harold** [[00:25:01](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1501)]
Yeah, I'll add a PR to put it in CI.

##### **Geohot** [[00:25:05](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1505)]
Cool. Yeah, I mean, if you assert a min speed, then it can be our responsibility to make sure that stays reasonably fast.

##### **Harold** [[00:25:12](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1512)]
Sounds good.

##### **Geohot** [[00:25:15](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1515)]
I think you guys are going to like the new export functionality when it comes to. It's going to be really easy to just save graphs. So yeah, I think we're going to have to do that. And I'll have to deal with the JIT stuff.

##### **Harold** [[00:25:24](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1524)]
Oh, it's not going to be a pickle anymore?

##### **Geohot** [[00:25:27](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1527)]
It's still a pickle, but it's a pickled UOP graph instead of a pickled captured JIT. I see.

##### **Harold** [[00:25:34](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1534)]
Yeah, that sounds a bit nice. I have one question, actually. When we moved to Rangeify, the compile speeds slowed down a lot, maybe like 5x or something. I mean, we can work around that, but is that something that's going to be improved ever? I don't really know why it happened, but I guess compile speed is something you guys care about?

##### **Chenyu** [[00:25:55](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1555)]
We care to the extent that people who use tiny graph cares. So if you have a benchmark or something and you say you want that to be something, then we will look into it. I mean, we know why it becomes slower, but.

##### **Harold** [[00:26:10](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1570)]
I see, but there's no fix on the roadmap until it becomes a user's priority.

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1577)]
Yeah, so I'm going to do some fixes for Lama, hopefully, this week. But these fixes won't apply to Kama's model. They're just fixes because Lama has a layer-based repetitive structure.

##### **Harold** [[00:26:30](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1590)]
Oh, I see. Yeah, OK. So if it's a problem, I'll make an issue and say what speed we would like.

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1599)]
Yeah, because these are generally,

##### **Chenyu** [[00:26:44](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1604)]
we are pretty tolerant on this front. Maybe we shouldn't, but we kind of know why this slow. And specifically for Renderfile, we make a trade-off saying, OK, this needs to be done. So if there's a speed regression, we will fix it later. Who knows what later will be? Wait till we merge eGraphs.

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1623)]
It'll all get two times slower, but better.

##### **Geohot** [[00:27:06](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1626)]
Sounds good.

##### **Chenyu** [[00:27:09](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1629)]
Slow compiles and fast runtime is a good trade-off, I guess.

##### **Chenyu** [[00:27:14](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1634)]
It's not really that. It's supposedly to make the code simpler.

##### **Chenyu** [[00:27:19](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1639)]
Oh, I see.

##### **Chenyu** [[00:27:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1641)]
Oh, no. No, so I think it would be a good idea if you just open an issue or something, saying you see the file that's, I mean, you say you measure that, and I believe you. But it would be nice to have this somewhere. And when we come to how fast this should be, we will use that as an example to the target.

##### **Harold** [[00:27:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1662)]
OK, I can open issue with that.

##### **Geohot** [[00:27:44](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1664)]
Yeah, if you say what it used to be. I mean, yeah, we know that Renderfile regressed things here. Sounds good.

##### **Chenyu** [[00:27:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1672)]
Yeah. Thank you for being a happy TinyGrad user.

##### **Harold** [[00:27:56](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1676)]
Yeah, I know. TinyGrad is much more beautiful than OpenCL code, so.

##### **Chenyu** [[00:28:02](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1682)]
Great. OK, next is my stuff.

##### **Chenyu** [[00:28:08](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1688)]
Also, I did some DevOps last week. I went through all the past two months of flaky AI tests, and root cause slow. So I saw there's another one that's new. That's a numerical thing on one of the new tests. But I think now it should be much better. All the assigned numerical tests use int. All the things that only crash on CI, I skip it. Something that's broken, I fixed. So I hope it's much better now. There are a few assigned tests that I really don't know. I don't know why it only crashed on CI. One hypothesis is there's one unit test that loads two gigs of memory. And our tests use about eight gig of peak memory. So if you've got unlucky distribution, maybe something would be bad. That's my guess.

##### **Geohot** [[00:29:14](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1754)]
What test uses eight gigs of memory?

##### **Chenyu** [[00:29:18](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1758)]
Oh.

##### **Chenyu** [[00:29:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1761)]
Gigs of peak memory, if you load things in a very bad order. Because there are a few tests that use gigs of memory.

##### **Geohot** [[00:29:30](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1770)]
We should figure out what's using all that RAM. So there's actually a limit. I have a limit of the buffer size. There's a limit for single buffer.

##### **Chenyu** [[00:29:37](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1777)]
But for example, our GUF test loads a model. And it loads a model in tiny grid. It also loads a model in ggml. Then it compares the output. So there's like 4x over here. So it's like a model in the RAM or something like that. Yeah.

##### **Geohot** [[00:29:56](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1796)]
So I don't know. I don't know if that's real.

##### **Chrism** [[00:29:59](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1799)]
I don't know.

##### **Geohot** [[00:30:04](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1804)]
Yeah. Hopefully, that's better.

##### **Chenyu** [[00:30:08](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1808)]
And assign set item. Continue to make progress on that. I removed some rules and paths and hacks in various places in schedule. And rangeify. And now I can move stuff from tensor.py, those contiguous, and realize gradually into rangeify that solves this. So eventually, yeah.

##### **Geohot** [[00:30:37](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1837)]
What did the I saw you change three items assigned to something else?

##### **Chenyu** [[00:30:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1842)]
Yes. I changed it to just make it an arc after you extract the shape steps.

##### **Geohot** [[00:30:50](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1850)]
So the movement ops become an arc?

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1852)]
Yes.

##### **Geohot** [[00:30:55](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1855)]
It's probably cleaner.

##### **Chenyu** [[00:30:58](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1858)]
I think it's much better that you don't need to allow this in spec and later have a hack somewhere saying, because for assign, the shape is the source of your assign, right? Previously, it was reading something else.

##### **Geohot** [[00:31:16](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1876)]
Yeah. I don't fully understand that hack. It's nice to see them getting cleaned up.

##### **Chenyu** [[00:31:22](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1882)]
Yeah. So now, I think once I finish the set item cleanup, it will mostly boil down to the realize game assign. So there are currently still allow some special bitcast assign for disk, because disk is special. And there's . So I'm going to use some legitimate use case for that, I assume, after something. So still some special pass for disk. I want to understand better. There's also this tiny FS regression I apparently made, and I reverted it later. It's nice that we have a way to test it in benchmark, but I still don't quite understand if that was a hack or a prefer worked around or something.

##### **Geohot** [[00:32:11](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1931)]
Can we test it in non-benchmark? Can we test it in CR?

##### **Chenyu** [[00:32:19](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1939)]
Can we test that in CI?

##### **Wozeparrot** [[00:32:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1941)]
At least we can test through the schedule stuff in CI. So that's actually what caught it, is the CI test caught it.

##### **Chenyu** [[00:32:30](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1950)]
Now we partially test it. We just don't test the execution.

##### **Wozeparrot** [[00:32:33](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1953)]
Yeah. We don't test the runtime in CI. We test the runtime in benchmarks.

##### **Geohot** [[00:32:38](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1958)]
Why can't we test the runtime in CR? Why can't we stand up a little tiny FS server? I guess we could.

##### **Wozeparrot** [[00:32:47](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1967)]
I don't know. There's a couple of parts to standing up a tiny FS server.

##### **Chenyu** [[00:32:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1972)]
If I break it later, then we discuss how to do. I think now scheduling is probably fine.

##### **Geohot** [[00:33:00](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1980)]
Yeah. OK, so.

##### **Chrism** [[00:33:07](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1987)]
Yeah.

##### **Chenyu** [[00:33:11](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=1991)]
Yeah, the other is the scope of, for now, we have some logic. So if something is realized, then realize it again. It won't change the output. But that's not true if you do a slice of sign to it. So there's some scope capture there. I have a hundred line. Complicated way to do that. I don't really like it. So I would think about that more. But I have something that removes all the realize in tensor.py and all the test paths.

##### **Geohot** [[00:33:45](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2025)]
It's just not very good. So let's look.

##### **Chenyu** [[00:33:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2032)]
I'm very excited about the remote.

##### **Chenyu** [[00:33:55](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2035)]
Yeah.

##### **Chenyu** [[00:33:56](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2036)]
So the eventual goal is, I think I said this maybe a week before or two weeks before, but disk should you just use regular assign paths so it can be lazy. Then we don't do any realize when we do schedule or just put a sign. So that's the goal.

##### **Chrism** [[00:34:15](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2055)]
OK.

##### **Geohot** [[00:34:17](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2057)]
If disk assign is the same thing, then that works. I've always thought that disk assign might actually be kind of different.

##### **Chenyu** [[00:34:27](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2067)]
There's no fundamental reason that should be different. Other than disk cannot do ALU. So anything you want to construct your source, you need to do that in other device.

##### **Geohot** [[00:34:40](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2080)]
Yeah. But disk also has this property where, like, you can't do that.

##### **Chrism** [[00:34:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2086)]
OK.

##### **Geohot** [[00:34:47](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2087)]
So you're ordering of, like, if you do two slice assigns, there's a real backing store. I guess I don't. I should read what you've done with the semantics of assign. Do we have a fixed set of understanding of what the semantics of assign should be? Yeah. That we do. Cool. And if you think it's the same as disk, then yeah. I just got to read this. Because we were never totally clear about what slice assigns. Even really means.

##### **Chenyu** [[00:35:20](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2120)]
Slice assign for now just means. So it's like in getItem, we have the view of a tensor versus, like, advanced getItem that returns a new tensor.

##### **Geohot** [[00:35:32](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2132)]
So for JIT. If I slice assign in a JIT, does it apply?

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2140)]
I think it should.

##### **Chenyu** [[00:35:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2142)]
But currently, we are not capturing that correctly. Got it. So basically, the output should be, my ground truth of output is it should give you the same output as eager output. Imagine you just add realize to every line.

##### **Chenyu** [[00:35:57](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2157)]
Yeah.

##### **Chenyu** [[00:35:59](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2159)]
The problem for JIT is the slice assign case, if you don't have explicit realize, we are not capturing that. Because it's not, like, in the output. That's pretty much the reason why we need to add realize everywhere in the front end.

##### **Geohot** [[00:36:15](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2175)]
Yeah. I mean. I think we can just kind of have a JIT thing that tracks all the assigned tensors as well.

##### **Chenyu** [[00:36:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2181)]
Oh, yeah. So there are two. I have two main solutions on this. One is build a dependency global-ish map, like all tensors, to track this dependency. I really don't like that. Another is to use some after structures to wrap everything. That is better.

##### **Geohot** [[00:36:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2202)]
But that's more complicated when you need to resolve this. After dependency. I see. Let me know if you want me to look over any stack. Yeah.

##### **Chenyu** [[00:36:56](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2216)]
So I think my priority would be if I can have a relatively clean way to do this with a global map that's, like, handle properly, I would probably merge that. I also want to explore just, like, try to make this structure into the after and this U up, then let the back end figure out. I think that's better. Yeah. But I think now we have pretty much all the cases. I also compare this with the task case for Torch and JAX and NumPy to make sure, like, everything, like, it won't be a surprise, basically.

##### **Geohot** [[00:37:33](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2253)]
Right?

##### **Chrism** [[00:37:35](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2255)]
Yeah.

##### **Geohot** [[00:37:35](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2255)]
Well, that's cool. OK. And that's my stuff.

##### **Chenyu** [[00:37:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2261)]
Next is assembly, I guess, also the core refactor.

##### **Chrism** [[00:37:45](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2265)]
OK.

##### **Geohot** [[00:37:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2266)]
Yeah. So I spent most of the last week on the call stuff. I'm very happy with where it ended up. We've removed two ops. So kernel and custom kernel no longer exist. And call is universal. You can put three things on the call. You can either put something that's at the tensor level, and that will basically just kind of lambda function to the tensor graph. So this is just a little bit of a test. This is useful if you want. Like, this is what I do with embedding. So if you want to, like, have the normal embedding forward, have a tensor graph, and replace the call early, you can do that. But you can still have a custom grad function on that. Call can also be used to define a custom program in uops. And that'll run the normal uop compiler flow on that. But it's already lowered down to the load store layer. The ranges are done for you, all that stuff. So that's like what TinyKittens is. And then the third thing is you can just have a completely custom program, and it just uses the program uop. And I think that this call thing, I added hooved, because it's finally the correct thing to do exports as renderers. So we could, like, export to WebGPU just entirely as a renderer. And I was thinking, I'm starting to think about how this could kind of even replace the JIT. I'm like, we're finally there. I have to do a little more cleanup. I want to clean up the schedule, Cath. All right. So I have scheduled, Cath, as a hack called lunique, which puts luniques on the buffers for local unique. This is nonsense. It should just be param. So then the entire schedule just becomes, all the inputs become params. And then everything is the same at every level of the hierarchy. I also need to add some tests to do calls at multiple levels. So like, it doesn't just, this can be a completely multi-level hierarchy. It doesn't just have to be a two-level hierarchy where you have, like, any concept anymore. It's more of like a schedule and then a kernel. It's just this thing with calls that can nest multiple layers deep. And the other thing should be able to handle that. So yeah, I mean, my goals for this week are to use parameters schedule cache, clean up the, make sure the multi-level call is correct, and then clean up and remove schedule item. Because we don't need schedule item anymore. That's just a uop graph. Yeah, so I'm happy with how things are progressing here. I spent this morning playing with eGraphs and playing with Mirage. Mirage is kind of the state of the art of mega kernel stuff now. Just looking at what they're doing and what we're still missing and what the new kind of optimization stuff is going to look like. But yeah, a whole bunch more call cleanup. On the assembly side of things, I mean, at some point, we just have to kind of decide extra AMD is good enough. I posted about it. Nobody replied. If anyone thinks the code is not good enough, I don't know if I'm in my agent psychosis era where I think it's good enough and it's actually awful. But I don't know.

##### **Chenyu** [[00:41:11](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2471)]
If you are happy with it, sure. I don't know. Are you happy with it?

##### **Geohot** [[00:41:15](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2475)]
I can certainly do more to clean it up.

##### **Chenyu** [[00:41:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2481)]
But it's not about if you can or cannot. Are you happy with that? If someone else take that PR and say merge this, will you click merge or not?

##### **Geohot** [[00:41:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2491)]
Probably not. And we can, yeah. Well, probably not without talking about it a bit more. What I am happy with with that PR is the API. Like I think the actual API and the DSL are very good. And that was all the part that was done by hand. The actual, like, particularly in files like this, like yeah, like it's AI slop, but it's just like it's a function. There's no other way to like implement. It's just like a lot of crap there. Yeah, I could probably clean it up. I could probably knock 100 lines off it. But I don't think I could make it any conceptually cleaner. So I think if someone else put that PR up, I would struggle for a while and be like, you can make this cleaner. You can make this cleaner. You can make this cleaner. And then I spent two weeks struggling to make it cleaner. And it's like, yeah, sure, I can make the code nicer, but I can't make the API nicer. So.

##### **Chenyu** [[00:42:26](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2546)]
Yeah, I mean, I think that's fine.

##### **Geohot** [[00:42:29](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2549)]
Yeah, I mean, I kind of think we just move it over. And you know, look, tinyGrad is a living code base. It's not like set in stone. But what I am happy with about it is I feel that finally, the decisions were made correctly about like how the DSL works, how the emulator works. And then like the SQTT and the DASASMR stuff, they're kind of crap, but like, who cares? Like, you know, OK, we can clean them up later. We don't like to keep it an extra. So yeah, I think that kind of merges. I gave T.

##### **Chrism** [[00:43:03](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2583)]
Yeah.

##### **Geohot** [[00:43:05](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2585)]
I gave T. Thompson feedback on x86 assembly. I mean, you know, he could. I struggled with the same stuff with the linearizer with him. I like the linearizer so much. I like the linearizer so much that I ended up doing the stuff myself to get it merged. I don't love this x86 assembly stuff this much. If he's excited about getting it merged, then he'll take my feedback. If he's not excited about getting it merged, then he won't.

##### **Geohot** [[00:43:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2611)]
OK.

##### **Geohot** [[00:43:34](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2614)]
But yeah, no, I do think there's some good stuff there. It's pretty fast, too. The x86 backend is pretty good. It's faster than, you know, the X86 backend. And without Beam. It's faster without Beam than playing. So I think it does a bunch of things right. But I think that we still have to deal with that ops thing. And I think the answer is something like ops ins, not massively polluting the ops space with like all the x86 instructions. And that'll also work with the RDNA 3 one as well. So yeah. OK, cool. I'll get extra. I'll just merge that stuff from x86. I'll get extra assembly. It's 4,000 lines. It's nice to not have it, not have to use Python path. It can ship with the thing. It can ship with TinyGrid proper.

##### **Geohot** [[00:44:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2671)]
And yeah, I mean, it's a full, if you think about how many lines AMD used to write basically that same thing, probably 100,000. So far than that. Yeah, I think those are fine. It's not as annoying as like some random functions in scheduler.

##### **Geohot** [[00:45:00](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2700)]
No, it's not. It's not. And it is well isolated. And that's not entirely an excuse. But it's the most important thing is complexity management. And the things in there that aren't perfect will not creep into complexity elsewhere in the code base. Yeah.

##### **Chenyu** [[00:45:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2721)]
So I mean, that's pretty much why it's fine to merge that. I think very similar reasons for a lot of like thousand lines of inclusion. Thousand lines of what? It's like when we add onX or something like that. Yeah. It's its own thing. So it's fine. Exactly. Exactly.

##### **Geohot** [[00:45:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2742)]
Okay. Sounds good.

##### **Geohot** [[00:45:44](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2744)]
Oh, it has a bunch of tests too. How do you feel about moving? So right now we have a lot of test files in test slash startup high. How do you feel about moving those to something like test slash, you know, like backend specific

##### **Geohot** [[00:45:57](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2757)]
or something like that?

##### **Chenyu** [[00:46:03](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2763)]
Oh, I mean, I don't, I don't have a strong preference as long as easy to discover the test.

##### **Geohot** [[00:46:13](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2773)]
I mean, it'll be another sub folder. So it won't be like test slash test ops anymore. It'll be like, you know, test slash E to E slash test ops.

##### **Geohot** [[00:46:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2791)]
Oh, or test slash integration slash test ops. I don't have a strong opinion on this.

##### **Geohot** [[00:46:43](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2803)]
Yeah. I mean, my only reason to do it is just so we can stop like using like dash dash ignore. Cause like right now we have all these like dash dash ignore models. Yeah.

##### **Chenyu** [[00:46:53](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2813)]
Yeah. I think just pick, pick one, pick maybe just have a cloud suggest something or see what other repos struck earlier test. It'd be fine.

##### **Geohot** [[00:47:05](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2825)]
Yeah. I'll do some research into this, but yeah, the reason I want to do this is so I can put the AMD assembly tests and like test. Assembly or something.

##### **Geohot** [[00:47:15](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2835)]
Oh, sounds good.

##### **Chenyu** [[00:47:25](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2845)]
Hey, so cause when it's not here, I think she put the updates in Lamar channel for things.

##### **Geohot** [[00:47:39](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2859)]
Then what else do we have? Oh, B1TG. You want to share something about FPA?

##### **Chrism** [[00:47:48](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2868)]
Oh,

##### **Geohot** [[00:47:50](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2870)]
Oh,

##### **B1tg** [[00:47:53](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2873)]
I was trying to add the FP eight hybrid mode, which is a ML puff train using. So I think this may be helpful for the ML proof. Submit.

##### **Geohot** [[00:48:17](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2897)]
Hi hybrid mode.

##### **Geohot** [[00:48:19](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2899)]
You mean using the float 32 flash attention and FPA jump.

##### **B1tg** [[00:48:27](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2907)]
Hi, the murder means in the back, backward, backward. There, there are two met male, the greater quantization. Yeah. So you can use the method to use, use E E two M five and the, and there's a forward, forward mat. May I use E four M three.

##### **Chenyu** [[00:49:06](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2946)]
Oh, so you was one FPA for forward and the other one for backward. I think a media. Like, so just this.

##### **Geohot** [[00:49:13](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2953)]
Three years ago.

##### **B1tg** [[00:49:18](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2958)]
Yeah. The MD ML puff. The Lamar train using this conflict.

##### **Geohot** [[00:49:26](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2966)]
I see. Yeah. We should be able to support it the same way we do the normal. Like, I think, I don't know if we have a flag explicitly for accumulate in, but you just need to put the caster on the expand.

##### **B1tg** [[00:49:41](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2981)]
The issue is.

##### **Chenyu** [[00:49:42](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2982)]
For now, our backward D type is always the same as the forward D type.

##### **Nimlgen** [[00:49:49](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2989)]
It shouldn't have to be. So if you put the cast around the expand.

##### **Chenyu** [[00:49:57](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=2997)]
So if your forward always wrong with the, say the. Mentes are two version. Then how can you know that in backward issue use the Menteza three version. Yeah.

##### **Geohot** [[00:50:10](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3010)]
You have to put the casting cast back around the expand. Right? So if you think about what a mat mall is, a mat mall is an expand a mall and a reduce. So in the forward pass, whatever data type that reduce has is going to be your, your reduction data type. But in the backwards pass, it's the expands that become reduces. So if you put a cast before the expand to what you want the backwards D type to be, and then you put the forward pass. And then a cast after the expand to put it back. Then when you go backwards through that, the expand becomes the reduce and it'll have the correct D type.

##### **Chenyu** [[00:50:48](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3048)]
Yeah. But wouldn't that means in your forward, you actually do the cast?

##### **Geohot** [[00:50:54](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3054)]
Well, yeah, but they should cancel out.

##### **Geohot** [[00:51:00](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3060)]
Cancel out with what? Each other. So we certainly don't do that automatically now. I know.

##### **Geohot** [[00:51:11](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3071)]
And we might want, we might want to.

##### **Chenyu** [[00:51:14](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3074)]
Okay.

##### **B1tg** [[00:51:15](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3075)]
I just use custom kernel to do this.

##### **Geohot** [[00:51:20](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3080)]
Yeah. It's fine, I guess. But no, I mean, I think we should make this work and we should add a, like a backwards D type flag to gem. This is the problem with custom kernel. Now that it's there, everyone's going to use it.

##### **Chenyu** [[00:51:37](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3097)]
Okay. I think, I think it would be nice to support this in customer kernel to start with. This is similar to flash attention. Once we understand how it works, we can think about how to upstream it to technically proper.

##### **Geohot** [[00:51:54](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3114)]
Yeah, it's fine.

##### **Geohot** [[00:51:55](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3115)]
It's fine to use custom kernel, especially if we're using custom items gems.

##### **B1tg** [[00:52:04](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3124)]
And I also need to reflect the pencil call to support different, different D type in. Currently the A and B of the same time. It's the mixed FP8 met mail.

##### **Geohot** [[00:52:30](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3150)]
Different FP8 type. So you can read the PR later. Sounds good. Hey, what else?

##### **Chenyu** [[00:52:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3172)]
Oh, what's up with the CPU Lama one B speed something, something, something. That's still a thing.

##### **Geohot** [[00:53:02](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3182)]
Oh, yeah. I mean, people are working on it. If they actually succeeded, I'll give them that bounty. They succeeded.

##### **Geohot** [[00:53:10](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3190)]
It was something that can be upstream. Because none of the attempt try beam. So I don't even know if I just run beam today. Is it faster? Is it not faster? That's crazy. That they're not using beam.

##### **Chenyu** [[00:53:35](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3215)]
I mean, I imagine the bounty is just find a way to run this model faster than porch. So before upstream any change to the behavior, we should benchmark with being. That's my thinking.

##### **Geohot** [[00:53:52](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3232)]
And not mess around with the heuristic.

##### **Geohot** [[00:54:03](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3243)]
My understanding is, yeah, I mean, this one that I see is making a custom map that kernel. I don't think beam gets it. I think I tried it with beam.

##### **Geohot** [[00:54:14](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3254)]
Yeah, but my point is, even with that, it's weird that it's not using beam to compare.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3261)]
I don't know. Oh, but if they write a custom kernel, they're not going to use beam. Yeah, but there are other parts of the thing.

##### **Geohot** [[00:54:30](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3270)]
Anyway. I bet you.

##### **Geohot** [[00:54:31](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3271)]
I bet you it's all the map back.

##### **Nimlgen** [[00:54:36](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3276)]
Oh, I have a change that erect the bandwidth for MOE for LLM.py.

##### **Chenyu** [[00:54:49](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3289)]
But I see a good number from growth. That number looks, the GPS number looks weird, even if you accounted for the 5x or something. I think it's a number for active experts, so I don't know what's happening there.

##### **Geohot** [[00:55:08](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3308)]
I bet that the GPS number fakes accessing all the experts.

##### **Chenyu** [[00:55:14](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3314)]
Oh, yeah, because even that, you divide that by six. I think that's a number for 4.7 flash.

##### **Geohot** [[00:55:22](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3322)]
It's still pretty high. I think you're getting 20 tokens per second. That seems good. Double that. bounty. Yep.

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3336)]
Yeah, I'm pretty happy with the progress on that. If we can actually beat Lava CPP for that, people might use it.

##### **Geohot** [[00:55:46](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3346)]
Mm-hmm. Do we have anything in bounty? Nope. Do we have anything in issue? I'm sorry. Okay. I think that's it for this meeting.

##### **Chenyu** [[00:56:13](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3373)]
Thank you, everyone. See you next week. Bye-bye.

##### **Chrism** [[00:56:17](https://www.youtube.com/watch?v=4xD6QrFdvYc&t=3377)]
Bye.
