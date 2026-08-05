# 2026-08-03 Meeting

### Meeting Agenda

**Time:** new meeting #31, 8/03 9am Monday San Diego time
- company update
- HCQ2
- MULTI, UNSHARD
- LLaMA training, MXFP4
- GPT-OSS training
- CONST weak dtype
- SLICE, Comma big model
- bounties, issues, Comma happiness, Kimi


### Audio

[Youtube Link](https://www.youtube.com/watch?v=cR5DnuwnCBw)

### Highlights

* **[USB GPU Dock Launch](#geohot-000008)**: A new external USB GPU dock is scheduled to launch August 12 for approximately $249–$299, featuring an aluminum chassis, serial and extra USB ports, an unbrickable design, and an optimized Qwen3-27B setup for the Radeon 7900 XTX.
* **[Token Box Product Vision](#geohot-000215)**: Geohot proposed a single-GPU “token box” that runs on a home network, serves inference over HTTP, displays token throughput and concurrent users, and competes economically with cloud APIs.
* **[HCQ2 Rollout](#chenyu-001021)**: The team expects to make HCQ2 the default for AMD and CPU during the week after adding the remaining DISK-copy, pinned-memory, and recovery-related functionality.
* **[MULTI Replaced by UNSHARD](#geohot-001055)**: MULTI has been removed and replaced by UNSHARD, a movement operation that inserts a device or warp range into a tensor shape to represent sharding across devices or GPU execution lanes.
* **[Rangeify Redesign](#geohot-001611)**: The new rangeify implementation will solve UNSHARD constraints rather than pushing movement operations through the graph, enabling the deletion of `pm_multi`, the final movement-op-pushing pattern matcher.
* **[Self-Optimizing tinygrad](#geohot-001747)**: The long-term plan is for tinygrad’s built-in LLM application to replace BEAM search with a small agentic loop that runs inside tinygrad and helps optimize tinygrad itself.
* **[MXFP4 Training Progress](#qazalin-001847)**: MXFP4 GEMM and quantization support has merged; the fastest run converged in 6,144 steps at 1.39 seconds per step, compared with AMD’s roughly 1.1-second reference on the same machine.
* **[GPT-OSS Performance Gap](#wozeparrot-003021)**: Sliding-window attention reduces step time from about 2.5 to 2.2 seconds, and MoE-routing work could bring it to 1.6–1.8 seconds, but the eventual target is approximately 500–625 milliseconds.
* **[CONST Weak Dtypes](#chenyu-003650)**: Work continues toward inferring every UOp’s dtype rather than storing it as an attribute; CONST now uses weak dtypes before late decomposition, with an effort underway to avoid storing dtype in the CONST argument entirely.
* **[SLICE and Comma Benchmarks](#chrism-004053)**: SLICE is expected to become simpler after resolving COPY and 64-bit-variable issues, while the new Comma small model has been added to CI and the big model is running in the USB GPU benchmark.
* **[Comma Big Model Ready](#chrism-004356)**: Comma previously reverted a tinygrad update because the large model was too slow, but the GPU implementation is now reportedly fast enough for driving, with further optimization potentially reducing execution to around 20 milliseconds.
* **[tinybox BMC Security Update](#geohot-004729)**: tinybox V2 systems need a BMC firmware update because a public CVE permits unauthenticated compromise; customers will be notified alongside a fix for network-card overheating, including an optional free fan or printable STL.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=0)]
Start with company updates.

##### **Geohot** [[00:00:03](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3)]
Let's see. What do we got this week?

##### **Geohot** [[00:00:08](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=8)]
Product launch, August 12th.

##### **Geohot** [[00:00:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=13)]
You guys are in this channel, so you guys can hear about it. We're shipping a USB GPU dock. I think it's going to be $249.

##### **Geohot** [[00:00:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=25)]
It's a lot nicer than the ADT-Link dock. It's unbrickable. You get a serial port and an extra USB port. This unbrickable dock is in a beautiful little aluminum chassis. I think you guys are going to love it if anyone's remotely considering an external GPU.

##### **Geohot** [[00:00:44](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=44)]
I have to confirm that it's $249. It's either $249 or $299.

##### **Geohot** [[00:00:49](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=49)]
But yeah, you guys are going to love it. And we're going to ship, out of the box, a fast Qwen3.6.

##### **Geohot** [[00:00:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=59)]
So this is Qwen3.6-27B, about 30% faster than anybody else has ever gotten it on a 7900 XTX.

##### **Geohot** [[00:01:12](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=72)]
And it's on par with a 3090, basically. So I got it on par with a 3090.

##### **Wozeparrot** [[00:01:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=81)]
Do we think Qwen3.8 is going to be the same architecture?

##### **Chenyu** [[00:01:23](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=83)]
Yeah, we might get Qwen3.8.

##### **Wozeparrot** [[00:01:24](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=84)]
Yeah, because we'd probably get Qwen3.8.

##### **Geohot** [[00:01:26](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=86)]
That would be awesome.

##### **Geohot** [[00:01:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=89)]
Yeah, even if it's not the same architecture.

##### **Geohot** [[00:01:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=91)]
What this is, is a lot of...

##### **Geohot** [[00:01:35](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=95)]
It's just the GGUF kernels. Codex wrote fast GGUF kernels that fully utilize the memory bandwidth.

##### **Geohot** [[00:01:44](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=104)]
And I've been shipping a whole bunch of quality-of-life improvements to the LLM server, too. I think the last one I have to land is the multithreaded one. Once it's multithreaded, it should kind of be on par with SGLang. I was looking into how SGLang works this weekend. It's not that hard.

##### **Geohot** [[00:02:01](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=121)]
Yeah, so... I mean, there's a few nice things it has that we won't, but... I think it's actually practical. Because long-term, what we should be thinking about is a product that's like a token box. We put one GPU, single-board computer.

##### **Geohot** [[00:02:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=135)]
That thing sits on your Tailscale, and it just provides you tokens over HTTP. It's the cloud in your house. That's who we have to be competitive with. If we want to sell tinyboxes to the GPU middle class, we've got to be competitive with the cloud APIs, basically.

##### **Geohot** [[00:02:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=151)]
You know, something that can pay for itself if you fully utilize the tokens in like a year. And then I think that will appeal to enough people, right? Like, we actually... We have a thing that we have to compete with, and it is the cloud APIs.

##### **Geohot** [[00:02:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=165)]
So, the token box. You know, imagine a tiny, tiny box that has a little screen that tells you the number of tokens per second, tells you the number of concurrent users.

##### **Geohot** [[00:02:54](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=174)]
Yeah, I think we could build a really nice product around that. And it would be great if we have Qwen3.8, because that might actually be smart. I mean, Qwen3.6 isn't stupid, but...

##### **Geohot** [[00:03:05](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=185)]
Wait. Oh!

##### **Geohot** [[00:03:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=187)]
Qwen3.8-27B.

##### **Geohot** [[00:03:10](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=190)]
Oh, perfect. Oh, this would be great. All right, cool.

##### **Geohot** [[00:03:17](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=197)]
So, yeah. Product launch, August 12th.

##### **Geohot** [[00:03:28](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=208)]
That's it.

##### **Chenyu** [[00:03:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=209)]
Great. Sounds good.

##### **Chenyu** [[00:03:32](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=212)]
I guess if we say we're going to launch with this, we will add this to CI later?

##### **Geohot** [[00:03:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=220)]
Yeah, we'll add it to CI. I also want to get this stuff merged.

##### **Geohot** [[00:03:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=225)]
It's mostly going to be one, like, 300- or 400-line kernel file. That's fast kernels for AMD, all written in the TinyRed language. So...

##### **Chenyu** [[00:03:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=239)]
Sounds good. Okay, that's the company update. Let's move on to HCQ2.

##### **Nimlgen** [[00:04:08](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=248)]
Yeah. So, I've been working on the Python optimization speed. Now, in master, it's a decent speed, so I'm going to switch all our CI training runs to HCQ2.

##### **Geohot** [[00:04:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=269)]
Instead of switching CI, can we just flip the default?

##### **Nimlgen** [[00:04:35](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=275)]
No, it's not ready. I mean, I need some recovery things and all this to make it compatible with HCQ1.

##### **Geohot** [[00:04:51](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=291)]
I think we should just flip it and make it the default. If it's at all ready, we should flip it and make it the default.

##### **Geohot** [[00:05:00](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=300)]
Okay, yeah. I mean, what's it going to take, right? Because the question isn't when can we get it in CI; the question is when can it be the default? And if people have to deal with a little bit more jankiness, well, that's on the people, right? I shipped rangeify long before it was ready. HCQ2 is really important, so...

##### **Geohot** [[00:05:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=318)]
You know, just be ready that when you do flip it, you're going to get a lot of bug reports, but I think that's good.

##### **Nimlgen** [[00:05:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=325)]
So actually, the missing part that I wanted to solve during this sprint is that we don't have all these fast copies from DISK and to DISK. We don't have all this copy optimization logic, like from DISK to DISK, and this pipelined logic where we copy in parallel to pinned memory and from pinned memory to the GPU. So I'm going to add these rules.

##### **Nimlgen** [[00:05:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=359)]
I think tomorrow, I think they should be quite easy. And after that, it should be good to make a default.

##### **Geohot** [[00:06:11](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=371)]
And then how about that cache change?

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=376)]
Hmm? Is there any reason we can't cache the sysmem?

##### **Nimlgen** [[00:06:22](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=382)]
Sorry, I don't get it.

##### **Geohot** [[00:06:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=385)]
It's the change that I posted in HCQ drivers.

##### **Nimlgen** [[00:06:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=389)]
Oh. No, I mean, it's good, yeah.

##### **Geohot** [[00:06:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=393)]
Because I'm really worried about flipping things like that and cache bugs. Like, I wonder if there's a reason why it's uncached.

##### **Nimlgen** [[00:06:42](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=402)]
Oh, I don't remember any reason. And if it should be uncached, like for the signals, it should have marked this uncached.

##### **Nimlgen** [[00:06:53](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=413)]
Yeah, that's what I think. So yeah, it should, yeah.

##### **Geohot** [[00:06:56](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=416)]
Cool. Okay, so copy optimizations aren't in yet. Yeah, I mean, get it... Okay, then get it in CI. Yeah, okay, maybe do flip CI first then.

##### **Geohot** [[00:07:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=424)]
But we really do need to switch it to the default as soon as possible.

##### **Nimlgen** [[00:07:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=435)]
So yeah, I've been working mostly on the Python optimizations. I also have a lower number of passes now. I think maybe...

##### **Geohot** [[00:07:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=445)]
Yeah, I saw that. That looks pretty good.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=459)]
And yeah, we're ready to move `ops_amd2` into the main codebase.

##### **Nimlgen** [[00:07:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=465)]
Yeah.

##### **Geohot** [[00:07:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=472)]
Yeah, so I'm looking at `hcq_compile` now. I think that's a reasonable number of passes.

##### **Geohot** [[00:08:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=487)]
Yeah, those all make sense to me.

##### **Geohot** [[00:08:09](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=489)]
I'm looking at, like, insert copy staging, schedule and merge HCQ, encode and pack, simplify patches, split patches, replace params.

##### **Nimlgen** [[00:08:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=513)]
And this has to run once for each JIT. I mean, it just runs once. When we create the JIT, we run one compile and one link, and after that we just execute them.

##### **Geohot** [[00:08:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=532)]
Oh, you've got link down here, I see.

##### **Geohot** [[00:09:00](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=540)]
Cool. That's a substitute and a resolve. That makes sense.

##### **Geohot** [[00:09:12](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=552)]
Sweet. Yeah, it's looking good.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=557)]
You know, I'm excited to delete HCQ.

##### **Geohot** [[00:09:22](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=562)]
HCQ2 looks about 100 lines shorter than HCQ.

##### **Nimlgen** [[00:09:28](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=568)]
Yeah, but it also includes all the functionality of the graph, which is several hundred lines more.

##### **Geohot** [[00:09:39](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=579)]
Yeah, I mean, I want to get rid of... Basically, I want to get rid of the JIT with this eventually. Once we have HCQ2, the JIT should just become a compilation. There shouldn't be a JIT that captures anymore; it should be a compilation JIT.

##### **Chenyu** [[00:10:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=613)]
Anything else?

##### **Nimlgen** [[00:10:16](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=616)]
No.

##### **Chenyu** [[00:10:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=621)]
Okay. So sometime this week, we will default AMD to HCQ2?

##### **Nimlgen** [[00:10:30](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=630)]
Yeah.

##### **Chenyu** [[00:10:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=633)]
And CPU?

##### **Nimlgen** [[00:10:37](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=637)]
And CPU, yeah.

##### **Chenyu** [[00:10:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=640)]
Yeah. Sounds good. Okay.

##### **Chenyu** [[00:10:44](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=644)]
Okay. Moving on to MULTI, UNSHARD.

##### **Geohot** [[00:10:55](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=655)]
Yeah. So, I did some work on... MULTI doesn't exist anymore. It's called UNSHARD.

##### **Geohot** [[00:11:03](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=663)]
UNSHARD is a better name than MULTI, but still not the final name. Right now, UNSHARD is a movement op that's kind of like the opposite of INDEX. If you think of INDEX as removing an axis and indexing it, usually using a RANGE, UNSHARD adds an axis back, usually using a RANGE. So we have a RANGE now called DEVICE. One of the axis types is DEVICE, which is a range across your devices, and then you can use UNSHARD to insert that range into the shape. So you can imagine if you have something that's size 16, rank one, and then you UNSHARD that across four devices, you end up with a tensor that's 4 by 16. That four represents the devices, right? You can then reshape that tensor to whatever you want.

##### **Geohot** [[00:11:50](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=710)]
And that'll just be your multi-device tensor. Now, the existing `pm_multi` is pushing UNSHARDs through the graph, but this is kind of an old way of thinking about things. We don't really push movement ops anymore, because it's very hard to push some movement ops through others.

##### **Geohot** [[00:12:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=734)]
For example, I'll tell you something you can't push. If you UNSHARD and then you flatten, you can't push in some cases, right? If you UNSHARD the middle dimension, or if you UNSHARD the first dimension and then permute them, you can't have non-multi-device, multi-device, non-multi-device represented in one axis. There's really no way to cleanly do this. I had a test branch where I did this using a factorization. You can factorize the shape and then have a list of its factors, right? So it's like four not on the multi-device, four on the multi-device, and four not on the multi-device, making a size-64 axis. But this was a lot to keep track of. So I thought about it a whole lot more, and what I really want to do is just extend rangeify to support UNSHARD.

##### **Geohot** [[00:13:06](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=786)]
And then what UNSHARD looks a lot more like is a constraint on the ranges. So, if you think about a normal rangeify, right? Let's think about a...

##### **Geohot** [[00:13:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=798)]
A matrix that's sharded across two devices, right? Rangeify always starts at the bottom. You slice the dimension that ends up being the sharded dimension, and you don't deal with that until you've made your way all the way up the graph. Then, when you're trying to INDEX into the UNSHARD, it says, "Hey, look, this dimension that you created further down needs to be split across the two devices."

##### **Geohot** [[00:13:47](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=827)]
So it then goes and solves for this, and it can't always be solved. You can have cases where, for example, you're doing an elementwise operation and one of them is sharded across axis one and one is sharded across axis zero. It's going to say, "I can't solve this," so you'll need to reshard it in some way. We can either use a heuristic for that or throw an error.

##### **Geohot** [[00:14:12](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=852)]
JAX throws an error.

##### **Geohot** [[00:14:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=854)]
So that's the new implementation of UNSHARD. It's coming with the new rangeify, but it's not dissimilar from the current UNSHARD. The current UNSHARD will insert as many ranges as you want at a list of axes, and it puts them on the front of the axis, as the outer part of the axis. But every arg, every movement op that's ever had an axis arg, always ends up getting the axis arg removed. That's going to happen with UNSHARD too once we're in the new system. Remember, REDUCE used to have a bunch of axes, but now REDUCE no longer has axes. It just has a number that says how many axes you're taking off the front, because you can always express this:

##### **Geohot** [[00:14:53](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=893)]
Okay, I want to REDUCE on axes two and four. You can express that as a PERMUTE where you put two and four on the front, then say, okay, I want to do a REDUCE where I remove the front two axes and reduce across them. It makes the semantics of the individual ops a lot simpler. So the final semantics of UNSHARD will just be the opposite of INDEX. It's range insertion, but at the front of the shape. Then rangeify will solve to make sure that it actually is unsharded across the dimension you gave it, which could be a DEVICE dimension or a warp dimension.

##### **Geohot** [[00:15:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=929)]
So you can also UNSHARD across the warp, and that's how you get `alloc_fragment`, right? Think about allocating a register on a GPU. You do `ALLOC REG`, but if that register is a VGPR, fundamentally, the way that's actually inside the GPU, that VGPR is sharded across the warp. So you would do UNSHARD and give it the warp dimension, and then you'd get 32, which is actually what the GPU is executing on. It's the same thing as multi-device, just a different layer. So eventually, probably maybe this week, realistically two weeks, we'll have the new rangeify in there, which is not very dissimilar from the old rangeify.

##### **Geohot** [[00:16:11](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=971)]
It's really the same rangeify; it's just easier to work on. It's mostly a refactor to make it easier to work on. That's solving for these things. Then we can delete all of `pm_multi`, which is the last of the movement-op-pushing pattern matchers. No more pushing movement ops. You just need to solve for movement ops.

##### **Geohot** [[00:16:28](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=988)]
So, yeah, that's that. And I'm doing some work on the LLM app.

##### **Geohot** [[00:16:32](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=992)]
I added some... It now says "interrupted," so the lines look nice. I fixed a few bugs in how Qwen parses the thinking tokens. You just want to make sure that you're always hitting the KV cache. I still have one more bug fix to go in for that.

##### **Geohot** [[00:16:48](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1008)]
Multithreaded would be very nice. Then figuring out how to actually get things to batch together is even harder than multithreaded, but multithreaded I think I can get merged. And then this demo example will hopefully be on Qwen3.8. I really hope they come out with Qwen3.8-27B and not the MoE version; then people are going to really want this.

##### **Chenyu** [[00:17:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1034)]
Yeah, I think that we will see when the weights are really out. Yeah.

##### **Chenyu** [[00:17:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1041)]
Cool. Should we eventually ship the LLM app as a separate thing?

##### **Geohot** [[00:17:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1051)]
I don't think so. And the reason I don't think so is, eventually what I want to do with the LLM app is replace BEAM search with it.

##### **Chenyu** [[00:17:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1065)]
I see. Okay.

##### **Geohot** [[00:17:47](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1067)]
Right. So you can imagine tinygrad having its own tiny little agentic loop that runs inside of tinygrad, hosted on tinygrad, that can optimize itself.

##### **Geohot** [[00:17:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1079)]
Yeah.

##### **Geohot** [[00:18:01](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1081)]
Okay. Yeah, I mean, I also think that it is part of tinygrad, because I think that the products that we sell should just be tinygrad alone. And if we want to sell a token box, you could imagine it just running tinygrad with a systemd service.

##### **Geohot** [[00:18:22](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1102)]
Yeah, so I think the LLM app stays a part of tinygrad. I think AI and LLMs are forever linked in people's minds, or at least for now.

##### **Chenyu** [[00:18:34](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1114)]
Okay. Sounds good. Anything else?

##### **Geohot** [[00:18:39](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1119)]
No.

##### **Chenyu** [[00:18:41](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1121)]
Moving on: LLaMA training, MXFP4.

##### **Qazalin** [[00:18:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1125)]
Yep.

##### **Qazalin** [[00:18:47](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1127)]
MXFP4 merged last week. So there is now an MXFP4 GEMM and quantizer. This is my fastest MXFP4 run, and it converged in the same number of steps as AMD.

##### **Qazalin** [[00:19:05](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1145)]
6,144 steps at 1.39 seconds. We need to get to 1.1 and below to surpass AMD. I have a branch that is already getting it faster.

##### **Qazalin** [[00:19:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1159)]
So I'll continue working on that one.

##### **Geohot** [[00:19:23](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1163)]
Oh, is this master, this 234?

##### **Qazalin** [[00:19:27](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1167)]
No, it's not. That's the problem. Master gets...

##### **Qazalin** [[00:19:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1173)]
It gets much worse. Mainly because the quantizer that I'm using is a tinygrad-generated quantizer. And the AMD one is fine. They started with Triton, but then they switched to this very complex-looking HIP kernel that uses a lot of `asm volatile`.

##### **Qazalin** [[00:19:54](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1194)]
I'll try to express it in UOps, but I think they went all the way to assembly because LLVM just can't describe those LDS transpose operations or whatever.

##### **Geohot** [[00:20:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1207)]
You can copy the kernel in if you want. You can just put the kernel in there.

##### **Qazalin** [[00:20:12](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1212)]
Yeah. I copied the kernel pretty much.

##### **Geohot** [[00:20:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1219)]
That's totally fine. What I don't want in a branch is a bunch of scheduler hacks. That's what I want fixed in master.

##### **Qazalin** [[00:20:28](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1228)]
Yep.

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1229)]
If you steal one kernel, I don't care.

##### **Qazalin** [[00:20:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1231)]
Yeah.

##### **Chenyu** [[00:20:34](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1234)]
So, there's a gap between master and this run. And there's still a 0.3-second gap from this run to the AMD one.

##### **Qazalin** [[00:20:43](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1243)]
We started a little faster. You have to factor that in.

##### **Chenyu** [[00:20:48](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1248)]
Yeah. And the chilled air that we need.

##### **Qazalin** [[00:20:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1252)]
So, our current difference with AMD is roughly 200 to 250 milliseconds. I'm pretty sure that at this point, if I just put a coding agent on it, it can make progress. This was from the weekend, going from 1.7-ish to this in two days.

##### **Geohot** [[00:21:16](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1276)]
Using a coding agent, or you doing it?

##### **Qazalin** [[00:21:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1279)]
A coding agent, just coding.

##### **Chenyu** [[00:21:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1281)]
Okay. And it can probably do it, right? Because AMD's run is already an existence proof that this is possible if you just go all the way down. It can just extract that all the way down and say, "This is it."

##### **Geohot** [[00:21:35](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1295)]
Yeah. I mean, that's why it's really important to have this stuff on master, right? You can get the speed with 10% of the work with a coding agent. The other 90% of the work is actually making it mergeable. I had those Qwen branches immediately that could get me the speed, but they were completely unmergeable. And now I've been slowly narrowing it down.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1319)]
Um... So, yeah. I mean, I don't care about beating AMD's time on the board. I care about beating AMD's time on our machine. So, what's AMD's time on our machine? Total time?

##### **Qazalin** [[00:22:11](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1331)]
AMD's FP8 total time?

##### **Geohot** [[00:22:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1333)]
No, FP4.

##### **Qazalin** [[00:22:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1335)]
Yeah.

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1337)]
Like, if we run AMD's fastest Docker on our machine, what do we get?

##### **Qazalin** [[00:22:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1341)]
Mm-hmm. I have the numbers here.

##### **Geohot** [[00:22:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1345)]
Okay.

##### **Qazalin** [[00:22:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1351)]
So, AMD got about 1.1 seconds per step on our machine.

##### **Qazalin** [[00:22:39](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1359)]
So, we have... I'll look at my total time and find that one, too.

##### **Geohot** [[00:22:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1365)]
Got it. So, what is this last 0.3? What's the slowness?

##### **Qazalin** [[00:22:53](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1373)]
Uh...

##### **Qazalin** [[00:22:55](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1375)]
Communications. I haven't looked into this much, but I profiled it, and our GEMMs and Flash Attention match.

##### **Geohot** [[00:23:06](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1386)]
Got it.

##### **Qazalin** [[00:23:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1387)]
They have different communication. They don't use our small SDMAs. They have a big one.

##### **Geohot** [[00:23:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1394)]
Bigger kernels?

##### **Qazalin** [[00:23:17](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1397)]
For all-reduce. We're doing a bunch of small all-reduces, and we're overlapping with compute. They have a different way.

##### **Geohot** [[00:23:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1409)]
Are they using SDMA, or are they using kernels?

##### **Qazalin** [[00:23:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1413)]
They're using SDMA. They have overlaps, but they're bigger. I haven't looked into this much, honestly.

##### **Geohot** [[00:23:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1420)]
I see. Oh, they're probably bucketing grads.

##### **Geohot** [[00:23:48](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1428)]
I mean, yeah, if they're bucketing grads, are we still doing the same thing? Do we still have, like, all the layers in a single tensor?

##### **Geohot** [[00:23:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1439)]
Oh, no, I guess we can't do that if we're overlapping it.

##### **Geohot** [[00:24:11](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1451)]
Okay, so I see that we're plus 138 milliseconds on quantization. Can we get rid of that?

##### **Qazalin** [[00:24:24](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1464)]
It's going to be some custom kernel stuff.

##### **Qazalin** [[00:24:27](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1467)]
Yeah.

##### **Geohot** [[00:24:27](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1467)]
Custom kernels for that are totally fine, even if you have to copy in HIP code. I don't care.

##### **Geohot** [[00:24:37](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1477)]
Like, that's a very isolated thing, right? Like, I really worry about, like, scheduler changes.

##### **Geohot** [[00:24:47](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1487)]
But if all we have to do is use `Tensor.custom_kernel` with some HIP code to do quantization, yeah, that's fine.

##### **Qazalin** [[00:24:55](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1495)]
Oh, yeah, there are scheduler changes, too.

##### **Geohot** [[00:24:58](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1498)]
Those are much higher risk, and I want to get those merged as soon as possible.

##### **Geohot** [[00:25:05](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1505)]
What are the E and R kernels that are adding 80 milliseconds?

##### **Qazalin** [[00:25:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1514)]
Those are scheduler bugs, yeah.

##### **Geohot** [[00:25:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1518)]
Those are what?

##### **Qazalin** [[00:25:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1519)]
I fixed most of those, yeah.

##### **Geohot** [[00:25:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1521)]
Oh, those are scheduler bugs, okay.

##### **Qazalin** [[00:25:23](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1523)]
Yeah, those are scheduler bugs.

##### **Geohot** [[00:25:26](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1526)]
Cool. So this 1.4 is with the quantization fix, too.

##### **Qazalin** [[00:25:32](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1532)]
Yes. This is actually quite old, honestly. Like, since then I've...

##### **Geohot** [[00:25:39](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1539)]
Do you have an update to that?

##### **Qazalin** [[00:25:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1540)]
I have not regenerated this, but, yeah.

##### **Geohot** [[00:25:47](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1547)]
Yeah, I mean, I'd be curious to see this compared to AMD's 1.1 second step. So if we're at, like, 1.4 and they're at 1.1, there's 300 milliseconds. We've got to find out where it is.

##### **Qazalin** [[00:26:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1564)]
Yeah.

##### **Geohot** [[00:26:06](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1566)]
All right, cool.

##### **Geohot** [[00:26:08](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1568)]
234 is not too bad. I mean, it'll be nice when we're below 211.

##### **Geohot** [[00:26:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1575)]
Because 211 is the fastest we ever did, right?

##### **Qazalin** [[00:26:20](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1580)]
215 is the fastest we ever did, yeah.

##### **Geohot** [[00:26:22](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1582)]
215 is the fastest we ever did.

##### **Qazalin** [[00:26:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1585)]
Yeah. It'll be nice when we're below that. I'm pretty sure we'll get there. So, I already have... I mean, I already have two iterations of the faster step.

##### **Qazalin** [[00:26:44](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1604)]
I haven't done a full training run that's faster than what I had posted there.

##### **Geohot** [[00:26:50](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1610)]
And then, yeah, feel free to kill Kimi whenever you want. Just put it back when you're done.

##### **Qazalin** [[00:26:55](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1615)]
Yeah. That's what I've been doing. And the AMD Docker is on the slower machine, but...

##### **Geohot** [[00:27:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1624)]
Well, I mean, I'm not worried about that. We can set, like, AMD reference times on both machines.

##### **Qazalin** [[00:27:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1633)]
Mm-hmm. Yeah.

##### **Geohot** [[00:27:16](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1636)]
Cool.

##### **Geohot** [[00:27:22](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1642)]
Anything else?

##### **Qazalin** [[00:27:24](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1644)]
No. I know you're worried about the scheduler merges. I'm going through them. I'm going through the removal of CONTIGUOUS from custom kernel run now.

##### **Qazalin** [[00:27:36](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1656)]
The good thing is that we have a baseline branch that gets a good schedule, even if the way it's getting it is kind of awkward. But, yeah, I think...

##### **Geohot** [[00:27:49](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1669)]
Yeah, the CONTIGUOUS on custom kernel thing. I mean, that PR you posted didn't look too bad.

##### **Qazalin** [[00:27:57](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1677)]
It's kind of wrong. I first didn't know it was wrong because CI was passing, but then I figured out the spec. Plus this is with Kimi, and it has edge cases. So, yeah, I mean, the scheduler work...

##### **Qazalin** [[00:28:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1694)]
The coding agents just aren't particularly useful here. I just have to...

##### **Geohot** [[00:28:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1699)]
No, they can't do anything there. It's not worth wasting time. I waste so much time trying to get them to do rangeify crap. They can't do it.

##### **Qazalin** [[00:28:28](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1708)]
Yeah. I'm not sure why, but it seems...

##### **Geohot** [[00:28:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1711)]
You just have to think it through, because they don't reason from first principles. Like they don't think about what I'm actually trying to build. They just type.

##### **Geohot** [[00:28:43](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1723)]
Which is like, again, if you're trying to make a kernel fast, turns out just typing, not a bad strategy. But if you're trying to, like, find the one line change that fixes the scheduler...

##### **Qazalin** [[00:28:57](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1737)]
Okay.

##### **Geohot** [[00:28:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1739)]
Sounds good.

##### **Chenyu** [[00:29:01](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1741)]
Let's move on to GPT-OSS.

##### **Wozeparrot** [[00:29:05](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1745)]
So everything that got our last convergence run should be merged into master, and then I added a CI test for it.

##### **Wozeparrot** [[00:29:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1758)]
It runs on NULL, and it's basically the same as the LLaMA one.

##### **Wozeparrot** [[00:29:22](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1762)]
Then I've been working on adding sliding-window attention to our Flash Attention.

##### **Geohot** [[00:29:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1769)]
Cool.

##### **Wozeparrot** [[00:29:30](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1770)]
It is almost 300 milliseconds faster.

##### **Geohot** [[00:29:35](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1775)]
What's the difference? 300 milliseconds faster than what? So what time are we at, and what time do we need? Can you also keep the fastest run you have at the top of the channel?

##### **Wozeparrot** [[00:29:48](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1788)]
Yeah. Okay. It's still our original run.

##### **Wozeparrot** [[00:29:51](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1791)]
Yeah.

##### **Geohot** [[00:29:56](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1796)]
So we're still at 9 hours.

##### **Wozeparrot** [[00:29:59](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1799)]
Yeah.

##### **Geohot** [[00:30:02](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1802)]
What do we think it'll be by the end of this week?

##### **Wozeparrot** [[00:30:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1807)]
Around 6 hours, I'm hoping.

##### **Geohot** [[00:30:09](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1809)]
Around 6 hours. Okay.

##### **Wozeparrot** [[00:30:11](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1811)]
Yeah.

##### **Geohot** [[00:30:12](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1812)]
I mean, this doesn't seem like... It doesn't seem like we're moving fast enough. Why is it still so slow?

##### **Wozeparrot** [[00:30:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1821)]
So, SWA cuts 300 milliseconds off our step. That goes from 2.5 to 2.2 seconds. And then there's something for MoE routing that I'm working on that cuts 600 milliseconds off the step. So that brings us to a 1.6- to 1.8-second step time.

##### **Geohot** [[00:30:44](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1844)]
Okay. But don't we need like under a second?

##### **Wozeparrot** [[00:30:48](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1848)]
We need 500 milliseconds. It is a long way to go until then. There's a bunch of custom kernels that still need porting over from LLaMA.

##### **Wozeparrot** [[00:31:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1864)]
But there's a bunch of stuff that we aren't doing right now that LLaMA is doing and that we could be doing, like fused loss, the SwiGLU fusion, and QKV fusion.

##### **Wozeparrot** [[00:31:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1875)]
None of this is happening in the current GPT-OSS.

##### **Geohot** [[00:31:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1879)]
Yeah. I mean, okay. So we need 625 milliseconds. We're still 3x off somewhere. This doesn't seem like tiny fusions.

##### **Geohot** [[00:31:32](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1892)]
It seems like we're just missing something pretty fundamental.

##### **Geohot** [[00:31:42](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1902)]
If we were 50% off, yeah, I could believe it's those kinds of fusions. But, like...

##### **Geohot** [[00:31:50](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1910)]
Why? Like, I don't understand where this gap is.

##### **Wozeparrot** [[00:31:54](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1914)]
I don't know.

##### **Wozeparrot** [[00:32:01](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1921)]
I mean, I asked basically all the coding agents when we were originally planning out the time. They all said this is basically pushing the machine to the max.

##### **Geohot** [[00:32:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1935)]
I mean...

##### **Wozeparrot** [[00:32:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1938)]
I've been kind of going off of that, and that this is a somewhat difficult time to achieve.

##### **Wozeparrot** [[00:32:30](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1950)]
I do know that our GEMMs are not hitting, theoretically, what a grouped MoE GEMM could hit, but it shouldn't be that much.

##### **Geohot** [[00:32:46](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1966)]
I mean, yeah, I'm just really confused. What do LLMs say when I ask them where the time is?

##### **Geohot** [[00:33:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=1994)]
Again, it can't be the GEMMs, right? The GEMMs aren't 3x off. If we were 50% off, I'd totally believe it's GEMMs and a bunch of little optimizations.

##### **Geohot** [[00:33:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2011)]
Is there some...

##### **Wozeparrot** [[00:33:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2013)]
You're missing 300 milliseconds to non-overlapped COPY.

##### **Geohot** [[00:33:38](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2018)]
Okay.

##### **Geohot** [[00:33:42](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2022)]
That's something. Do you think it's all just little things like this, or do you think we're doing something kind of fundamentally wrong?

##### **Wozeparrot** [[00:33:49](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2029)]
I do think it's all just little things. I don't think we have something fundamentally wrong.

##### **Chenyu** [[00:33:55](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2035)]
So, let's say 1.8 to 0.6. There's a 1.2-second difference, and let's say one trick gives you 0.3. You believe there are about five of these tricks?

##### **Geohot** [[00:34:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2053)]
Yeah.

##### **Chenyu** [[00:34:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2058)]
Okay.

##### **Geohot** [[00:34:20](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2060)]
Yeah. If that's what it is, then that's what it is. But okay, cool. So we're still on track to hit 1.8 this sprint?

##### **Wozeparrot** [[00:34:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2065)]
Yes.

##### **Geohot** [[00:34:27](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2067)]
Great. Yeah, we'll get to 1.8.

##### **Wozeparrot** [[00:34:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2069)]
I haven't discovered it yet. It's like I'll go along and then find out later that something is very wrong. But so far I have not hit this, and it just seems like it's a bunch of little things.

##### **Chenyu** [[00:34:42](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2082)]
Okay. So, I mean, if that's what it is, that's what it is. I think it would be nice, as part of doing this, to make it more obvious what tricks save us how much time, and we should see if it's really a lot of small tricks like this.

##### **Geohot** [[00:35:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2107)]
Yeah.

##### **Geohot** [[00:35:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2113)]
Interesting. But yeah, hopefully we get 1.8 this sprint, and then put together where our time is going. And see if you can figure out where NVIDIA's time is going, right? Because NVIDIA is actually surpassing these times.

##### **Geohot** [[00:35:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2133)]
It sucks that we don't have an existence proof for AMD, but NVIDIA is doing it. I don't know, is NVIDIA doing something that we can't do, or that we're not doing?

##### **Chenyu** [[00:35:46](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2146)]
Yeah, I think, let's say this is what it is, and that's the difference between 0.6 and 1.8. We should still be able to have a report or some understanding of roughly where these 0.3-second or even smaller cuts come from in the different parts, right?

##### **Chenyu** [[00:36:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2173)]
And I think it's valuable to know that. Otherwise, it's very hard to believe one way or another. If we are really doing something wrong, it's better to know it earlier rather than later.

##### **Geohot** [[00:36:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2185)]
Yeah.

##### **Chenyu** [[00:36:28](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2188)]
Sounds good. Okay. Anything else?

##### **Chenyu** [[00:36:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2200)]
Okay. Next is my thing. I spent most of the week on CONST weak dtype.

##### **Chenyu** [[00:36:50](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2210)]
To recap: currently, we have dtype as part of the UOp attribute, and we want to make the dtype of a UOp inferred from the UOp. The biggest offender is CONST, because CONST currently does a lot of things depending on what its dtype is supposed to be.

##### **Chenyu** [[00:37:17](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2237)]
So the current status is: before we do dtype decomposition in late codegen, every CONST has a weak dtype.

##### **Chenyu** [[00:37:34](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2254)]
There are a lot of complexities in dtype codegen, sorry, dtype decomposition, and some backends treat CONST slightly differently, notably x86.

##### **Chenyu** [[00:37:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2272)]
So, one practical way to do this is to say: currently the CONST arg is just the number you put in that CONST. One practical way is to also add dtype to it. The arg would effectively be the CONST value and its dtype. Ideally it should be all weak, but if we want a strong dtype for CONST, we can do it that way.

##### **Chenyu** [[00:38:26](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2306)]
That was my practical proposal last Friday. But over the weekend, I think I found another way to do things without it. So I will try for another two days before I give up.

##### **Geohot** [[00:38:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2320)]
I mean, yeah. It would be great if we don't need it. I did that `.val` refactor, which I think is a good refactor regardless. Using `arg` is just asking for bugs.

##### **Chenyu** [[00:38:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2332)]
Yeah. Yes.

##### **Chenyu** [[00:38:58](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2338)]
That's pretty much the CONST part. I want to get it into a good state by the end of this week before I go traveling.

##### **Chenyu** [[00:39:08](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2348)]
Also, previously in the rewrite engine, we stamped the old dtype onto the new UOp when we rewrote it. If we are going to remove dtype from UOp and make everything inferred, there's no dtype for us to stamp. I think there are currently four ops that still violate these rules. Three are things like CUSTOM, CUSTOMI, and PYLITERAL. I don't know what that is, but those should probably just change to `dtype=None` and infer from the source, and it would be fine. The last one is INDEX.

##### **Chenyu** [[00:39:58](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2398)]
There is some image coalescing stuff with INDEX.

##### **Geohot** [[00:40:05](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2405)]
Yeah. I know how to fix those ones. I mean, it would be great if we could do it without dtype in the CONST arg, and CONSTs really just don't have dtypes. I think that would be a big win.

##### **Chenyu** [[00:40:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2414)]
Yes. So I think I will focus on that. I really need to understand how late memory coalescing and late decomposition work. Everything tries to have some part early and some part late. I just need to understand this better.

##### **Geohot** [[00:40:36](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2436)]
Yeah.

##### **Chenyu** [[00:40:38](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2438)]
I think that's pretty much it. I also fixed a bunch of small things left and right when I saw them, but nothing too major. And with that, we can move on to SLICE, or I guess Comma big model.

##### **Chrism** [[00:40:53](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2453)]
Yeah. So last week, the only thing I did for SLICE was the 64-bit variables. I'm hoping to get SLICE out, hopefully today. It should be a lot simpler now.

##### **Chrism** [[00:41:08](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2468)]
I think the only things I was running into previously were COPY and 64-bit stuff, so it should be easy to square that away.

##### **Chrism** [[00:41:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2478)]
But yeah, most of the stuff I worked on last week was benchmarks, like updating benchmarks. We have the new Comma small model in CI, which I labeled as 0.11.2. That's not technically accurate, but I didn't really know what to call it because it hasn't been released.

##### **Chrism** [[00:41:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2500)]
And the big model is also tested on the USB GPU benchmark, Comma.

##### **Chrism** [[00:41:50](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2510)]
If you look at stats.tinygrad.win, you can see that it oscillates between two different speeds based on where it's running.

##### **Geohot** [[00:42:03](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2523)]
That's a lot.

##### **Chrism** [[00:42:03](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2523)]
Yeah. So the slow ones are C5, and the fast ones are running on C6. Why? I don't know. I noticed this morning, and I need to look into what's going on there.

##### **Geohot** [[00:42:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2535)]
Interesting. I mean, is it the GPU? Is it the USB copies?

##### **Chrism** [[00:42:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2539)]
It's not the copy speed. We benchmark the copy speed in the USB GPU benchmark, and they appear to be the same. So I'm not sure.

##### **Chrism** [[00:42:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2551)]
But yeah. Anyway, I'll try and look into this.

##### **Geohot** [[00:42:34](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2554)]
Oh, IR3 is a lot slower.

##### **Chrism** [[00:42:35](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2555)]
That is also true. I have not looked into that at all.

##### **Chenyu** [[00:42:41](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2561)]
Maybe swap the two external GPUs and let it run for some time, so we can draw more conclusions without you looking.

##### **Chrism** [[00:42:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2572)]
Yeah.

##### **Chrism** [[00:42:54](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2574)]
Did you ever update the kernel on C6, or is it still running the old kernel?

##### **Wozeparrot** [[00:43:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2584)]
No, I thought you were going to do C6. Oh, that might be it.

##### **Chrism** [[00:43:08](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2588)]
Oh, no. I only updated C5. So it's possible that the new kernel... I mean, we needed the new kernel to get it to be stable at all, but I wonder if the new kernel, compared with our very old kernel, clocks higher.

##### **Geohot** [[00:43:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2605)]
Clocks higher? We're seeing the opposite.

##### **Chrism** [[00:43:32](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2612)]
We're seeing worse performance with the new kernel. Although, it may be that the fact that this device requires the new kernel means it has some sort of USB issue that causes it to be slower.

##### **Chrism** [[00:43:46](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2626)]
It's not clear to me what the issue is, and I need to spend some more time looking into it.

##### **Chrism** [[00:43:56](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2636)]
The whole point of that was that Comma had to revert a tinygrad bump because the big model was slow. It is now apparently fast enough to drive on.

##### **Geohot** [[00:44:16](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2656)]
The big model on the GPU?

##### **Chrism** [[00:44:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2658)]
Yeah, the big model on GPU.

##### **Chrism** [[00:44:24](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2664)]
Anyway, that's mostly it. I'm going to look a little bit more into what's going on here.

##### **Chrism** [[00:44:35](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2675)]
Yeah. And then I also looked into it: if I run it with BEAM on my laptop, I can get it to run in 20 milliseconds.

##### **Chrism** [[00:44:42](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2682)]
So, in theory, we could get it to be even faster.

##### **Chrism** [[00:44:46](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2686)]
But apparently this is fast enough, so I haven't been optimizing that anymore.

##### **Geohot** [[00:44:51](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2691)]
I mean, that's slow too. Why is it three minutes and 40 seconds for pickle?

##### **Geohot** [[00:44:58](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2698)]
I mean, just look at the copy speed. I think... I don't know. I don't remember a COPY, or... I mean, I wish that pickle load was more broken out. Show me what that time actually is.

##### **Chrism** [[00:45:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2718)]
The copy speeds are the ones at the bottom there.

##### **Geohot** [[00:45:23](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2723)]
I wonder. We should be able to see from the CI if this problem is enqueue time or...

##### **Chrism** [[00:45:31](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2731)]
Yeah. Let's see if we can find a run on the other one.

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2741)]
That's the fast one too.

##### **Chrism** [[00:45:44](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2744)]
C6 is the fast one.

##### **Chrism** [[00:45:51](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2751)]
I'm not totally sure what the story is. I noticed this morning, so I haven't looked into it in great detail. But that's it.

##### **Chenyu** [[00:46:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2764)]
Okay, sounds good. Yep, let's move on.

##### **Geohot** [[00:46:16](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2776)]
I have one more company update thing.

##### **Geohot** [[00:46:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2781)]
We need to update the BMC on all the tinybox V2s, at least.

##### **Geohot** [[00:46:32](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2792)]
So I got locked out of a tinybox V2.

##### **Geohot** [[00:46:37](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2797)]
You should also fix this in the setup.

##### **Geohot** [[00:46:42](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2802)]
If you press no SSH keys, it deletes the provisioning SSH key, and you can easily lock yourself out doing this.

##### **Geohot** [[00:46:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2812)]
So it should just have a warning if you press no SSH keys or something that says you're going to do that.

##### **Wozeparrot** [[00:46:57](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2817)]
Provisioning SSH key isn't supposed to be publicly used. The whole point is that the key is immediately deleted so that people don't assume that we have a backdoor on their boxes.

##### **Geohot** [[00:47:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2827)]
Yeah, well, that's okay. That's not the main problem. The main problem is there is a backdoor on their boxes, and it's in the BMC.

##### **Wozeparrot** [[00:47:17](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2837)]
Yes, I'm already fixing this. So on new boxes, we will flash the BMC on V2s. I'm looking into V1s, but so far it is beta firmware only.

##### **Geohot** [[00:47:29](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2849)]
Yeah, I mean, let's just make sure we do it on the V2s. We should also include it in our email. We're going to send an email to all the tinybox buyers about the network-card overheating issue, which we now have a fix for: just a fan. I'm going to send a free fan to anyone who wants it, or post the STL. And we should also say to everybody in the field: update your BMC. The BMC has a CVE that makes it totally ownable, even with no credentials. And Kimi can do it. So, yeah.

##### **Geohot** [[00:48:02](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2882)]
I was shocked. I was shocked how bad these things are.

##### **Chenyu** [[00:48:09](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2889)]
Or how Kimi is.

##### **Geohot** [[00:48:12](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2892)]
It's a CVE. I mean, it's not like Kimi found a new exploit, right? It just used a publicly available CVE, but yeah.

##### **Chenyu** [[00:48:21](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2901)]
Yeah.

##### **Chenyu** [[00:48:24](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2904)]
Is Comma happy? I think they are pretty happy. I mean, we are helping them a lot because this is like pre-launching and launching the thing together.

##### **Chrism** [[00:48:32](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2912)]
Yeah. I have to double-check that they actually merged the new big model and, with that, bumped tinygrad. But I think they're happy about that. Yassine mentioned that he had a couple of issues driving and was unsure if these were tinygrad-related issues or Comma-related issues.

##### **Chrism** [[00:48:51](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2931)]
And yeah, I told him to let me know if they're tinygrad-related.

##### **Chrism** [[00:48:57](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2937)]
He was complaining about the way that we check LTSSM.

##### **Chrism** [[00:49:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2944)]
I need to look into that. I'm not sure exactly what he meant by it.

##### **Chenyu** [[00:49:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2947)]
But I think for any complaint that's about tinygrad, they should definitely open an issue.

##### **Chrism** [[00:49:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2953)]
Yeah.

##### **Chenyu** [[00:49:15](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2955)]
Not just complain.

##### **Chenyu** [[00:49:18](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2958)]
The firmware is kind of a joint project. Yeah.

##### **Chenyu** [[00:49:23](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2963)]
So I think there's definitely something that doesn't belong to tinygrad, and I don't know if we should spend more time proactively helping them.

##### **Chrism** [[00:49:35](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2975)]
Yeah. The thing he was complaining about was the way that we check LTSSM in tinygrad.

##### **Geohot** [[00:49:46](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2986)]
Oh, I didn't know we checked that in tinygrad.

##### **Chrism** [[00:49:49](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2989)]
We check it, and then if it's not set, we power on the GPU and check it again.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=2994)]
We need to just have firmware. We need to have an API for this. Have we deleted the non-custom firmware path yet?

##### **Chrism** [[00:50:02](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3002)]
I think so. Yeah.

##### **Geohot** [[00:50:05](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3005)]
Okay. Well, we should check that, delete the non-custom firmware path, and add the API to the custom firmware to query GPU stats.

##### **Chenyu** [[00:50:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3013)]
Yeah. Or however we query the power, or whatever.

##### **Chrism** [[00:50:19](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3019)]
Anyway. Yeah. That's probably the right way for him to communicate the issues that he's having is to open issues.

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3026)]
We shouldn't be poking the LTSSM. We should design an API that would be valid on both an ASM chip and a non-ASM chip.

##### **Geohot** [[00:50:36](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3036)]
I don't want to ever deal with poking registers again. That should not be in tinygrad.

##### **Chrism** [[00:50:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3045)]
Other than that, I haven't heard any complaints.

##### **Chrism** [[00:50:48](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3048)]
I think they're happy.

##### **Chenyu** [[00:50:52](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3052)]
Okay. Great.

##### **Chenyu** [[00:50:55](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3055)]
I don't see the people doing bounties here, but I imagine they're progressing on LLM and RDNA3.

##### **Geohot** [[00:51:13](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3073)]
Yeah, I merged the linear-attention PR. I see a DeepSeek V4 PR from b1tg. I'll review the symbolic shape and UOps later, also from b1tg. I see.

##### **Geohot** [[00:51:56](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3116)]
I'm looking at the "fix AMD WMMA" thing instead of...

##### **Geohot** [[00:52:06](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3126)]
It just skips tests. It shouldn't skip tests. I don't know why we need to test a 128 by 128. We should be able to test the minimum thing that's just like four tensors or whatever, or four TCs or something. Not huge.

##### **Chenyu** [[00:52:26](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3146)]
Okay. I don't know. We're probably going to bump the line count.

##### **Geohot** [[00:52:39](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3159)]
Yeah, we can bump the line count. That's fine.

##### **Chenyu** [[00:52:42](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3162)]
What's the increment we use? 1,000?

##### **Geohot** [[00:52:45](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3165)]
1,000 sounds good. Yeah, I need some of those lines for my AMD slop kernels.

##### **Chenyu** [[00:52:51](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3171)]
Okay, maybe you bump it when you are merging your slop kernels.

##### **Geohot** [[00:52:56](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3176)]
Yeah, but we can bump it by 1,000. We're going to delete so much stuff for HCQ. We have two HCQs in there now; we only need one.

##### **Chenyu** [[00:53:04](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3184)]
It's not that much, but okay, sure.

##### **Geohot** [[00:53:07](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3187)]
No, HCQ and all the graph shit, that's a lot. That's going to be 1,000 lines deleted.

##### **Chenyu** [[00:53:14](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3194)]
Okay. Anyway.

##### **Geohot** [[00:53:16](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3196)]
And rangeify is going to delete lines. Everything is going to delete lines. Slop kernels are fine; slop kernels are just going to be in one file.

##### **Chenyu** [[00:53:25](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3205)]
Yeah, I don't know. Okay, whatever. Replace with new line.

##### **Geohot** [[00:53:33](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3213)]
We'll eventually chip away at slop kernels. We'll get the codegen to generate the slop kernels.

##### **Chenyu** [[00:53:40](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3220)]
Sure, that would be nice.

##### **Chenyu** [[00:53:43](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3223)]
Okay. I think that's pretty much it for this meeting. Anything else?

##### **Geohot** [[00:53:47](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3227)]
Nope.

##### **Chenyu** [[00:53:50](https://www.youtube.com/watch?v=cR5DnuwnCBw&t=3230)]
Cool. That's it for this meeting. Thank you, everyone. Bye. Bye. Bye.
