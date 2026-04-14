# 2026-04-14 Meeting

### Meeting Agenda

**Time:** new meeting #15, 4/13 9pm Monday San Diego time
- company update
- tensor uop mixin
- llm app, new USB driver
- viz
- HCQ/AMD/USB
- llama
- new DEV
- bounties, issues, Comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=l2GRAx-2V-M)

### Highlights

- **[Company update / Chestnut launch timing](#geohot-000011)**: The external USB GPU dock “Chestnut” got strong interest from a recent video, and the team is aiming for a launch around **June**, with LLM benchmarks planned for the Chestnut page.
- **[LLM app usability improvements](#geohot-000115)**: Geohot said `JIT_BEAM=2` should not be required knowledge for users; the plan is to precompile kernels, add a progress bar, and potentially make the faster path the default to improve usability.
- **[Tensor `UOp` mixin refactor progress](#chenyu-000241)**: Chenyu has already moved much of tensor functionality into mixins, with `const`/`arange` and indexing-related behavior remaining as the main blockers before most methods can move over.
- **[`UOp`/Tensor boundary clarified](#geohot-000548)**: Geohot said only `Tensor` objects should resolve values like `.item()`, while anything involving scheduling should stay in `tensor`, not migrate into `UOp` mixins.
- **[New USB driver is done and much cleaner](#geohot-000810)**: Geohot reported the new USB driver/firmware is complete, simpler, and easier to test, including running RDNA 3 hardware tests with `DEV=USB+AMD`.
- **[Comma 4 USB instability likely tied to PD/orientation](#geohot-001013)**: During debugging of Comma 4 issues, the team suspected USB-PD negotiation and cable orientation handling as likely causes of inconsistent enumeration and “cable is bad” failures.
- **[Firmware emulator is now a serious debugging tool](#geohot-001161)**: Geohot highlighted that the emulator can run firmware on a computer, emit MMIO traces, and even emulate an NVMe drive well enough for it to appear as `/dev/sda`, making bring-up/debugging much easier.
- **[Qwen 3.5 merged; `rangeify` needs cleanup](#geohot-001292)**: Qwen 3.5 support was merged into the LLM app, but Geohot said `rangeify` is conceptually broken around `STORE`/`AFTER` and likely needs a clean, slower rewrite before re-optimizing.
- **[Viz got major speedups and new kernel-analysis direction](#qazalin-001618)**: Viz server/UI rendering got substantially faster after removing `O(n^2)` behavior, and the team discussed shifting toward cached pickle/debug reconstruction instead of repeated CLI calls.
- **[Agent-written HIP kernel beat Beam on FP8 quantize](#qazalin-001766)**: Qazalin reported that a Codex-written HIP kernel for FP8A quantization is about **1.5x–2x faster than Beam**, showing the promise of agent-assisted kernel optimization.
- **[LLaMA training time improved to about 3 hours](#geohot-001861)**: Geohot noted the team is now around **three hours** on LLaMA, and discussion focused on the remaining bottlenecks needed to push below two hours and potentially challenge AMD’s performance.
- **[New `DEV` syntax landed, but integration remains](#chrism-003332)**: Chrism said the new `DEV` syntax is implemented, with remaining work centered on integration, documentation, better error messages, and making mock GPU/device combinations cleaner.
- **[Preparing for users and release hardening](#geohot-003910)**: Geohot emphasized that “the users are coming,” prompting discussion of release readiness, dependency cleanup, and removing the current dependence on downloading headers from the internet before the next release.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=0)]
Let's start with company updates. So I think the biggest thing that happened this week was that video.

##### **Geohot** [[00:00:11](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=11)]
215,000 views. That's nice. So a lot of people are excited about the external GPUs. I think that the LLM software will be pretty good when we launch the hardware. So it'll all work pretty nicely together. We'll have some benchmarks for the LLMs that we put on the Chestnut page. Chestnut is an external USB GPU dock.

##### **Nimlgen** [[00:00:41](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=41)]
That's the main, that's the main updates.

##### **Geohot** [[00:00:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=43)]
We're going to sell a product for the masses. People still need to buy a GPU. Well, of course, I'm going to sell you a GPU. Don't buy an Intel GPU. That's a ripoff.

##### **Chenyu** [[00:01:03](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=63)]
I think most people are saying the speed is bad because they don't know how to make it fast. I don't know if we should use that for defaults or something.

##### **Geohot** [[00:01:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=75)]
Yeah, well, I mean, it's like it's our fault. Nobody should have to know that you have to just put `JIT_BEAM=2`. But I think also that even with `JIT_BEAM=2`, it doesn't give any feedback. And then `DEBUG=2` is too spammy. So I think we just need to change everything to compile the kernel beforehand and then give a progress bar that's compiling the kernels and that kind of stuff. Yeah, I think it would be OK to make it the default, or like `SERVE`, but then we would have to...

##### **Geohot** [[00:01:51](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=111)]
Yeah, give progress bar.

##### **Nimlgen** [[00:01:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=115)]
Yeah, that makes sense. There's also. Like not many kernels anyway. It would be fast.

##### **Chenyu** [[00:02:01](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=121)]
Or hopefully it's fast.

##### **Geohot** [[00:02:04](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=124)]
It's not that fast. I mean, this is another problem. Like JIT Beam is really slow. A beam is really slow because it spends a ton of time on stupid kernels. Like it spends a ton of time on kernels that spill. And then like it's not really easy to know if they're going to spill. There's no like easy way in UOPs. So you have to really detect that. And then it takes forever to compile them. And that takes forever to run them. So the JIT Beam with assembly will be fast. Like if we have an assembly, if we have an RDNA assembly back end that just asserts if the register allocator says, sorry, it doesn't fit the register allocator. The problem is like there's no way in like hip or something to say don't. Maybe there is actually. Actually, is this flag? We can pass. Yeah. To LLVM to say don't spill registers. Just fail. Yeah, I think I think if we could configure LLVM to bail out early, then also we should look into it. Just if no one's really looked into it, but we could make Beam 10x faster. And then I feel a lot with 10x faster and a progress bar. This suddenly becomes like really usable.

##### **Qazalin** [[00:03:27](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=207)]
Yeah.

##### **Nimlgen** [[00:03:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=208)]
Oh, when is when are we going to launch this thing? June.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=213)]
Yeah, probably June.

##### **Chenyu** [[00:03:35](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=215)]
Okay, we can probably think more of all this between after MLPerf and before the launch of that to improve the usability and app.

##### **Geohot** [[00:03:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=226)]
Yeah. I'll be back in San Diego soon. Hey.

##### **Qazalin** [[00:03:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=233)]
Oops.

##### **Nimlgen** [[00:03:56](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=236)]
Hey. Next is my item.

##### **Chenyu** [[00:04:01](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=241)]
So, tensor `UOp` mixing. I moved lots of stuff to mixins already. There's this big `OpMixin` that is basically a new `tensor.py` with all the functions. So now there's like 500 lines there. One of the annoying remaining things is `const`, because `const` blocks `arange`, and `arange` blocks everything that we do with indexing and stuff. So I'm still thinking about different ways to do it. The issue is unique const. We previously needed unique const because if we set the const to be the weight, then we don't want to link these tensors.

##### **Geohot** [[00:05:05](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=305)]
Otherwise, accumulating gradient is wrong.

##### **Chenyu** [[00:05:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=307)]
And it's just annoying because it's very hard to notice when you write it, but then `UOp` is immutable and cached. Also, one of the important invariants that I use is: when you build a tensor and you call a method on that tensor, it should be equivalent to calling that method on the underlying `UOp`, because eventually we want tensor to be a wrapper of the underlying `UOp`, like a very thin layer. So I have been using that invariant to move things like `add` and `getitem`, making sure it's the same. But this just isn't true right now for creation, because I don't think we want the underlying `UOp` to be different every time we call it. So one direction I'm thinking is to move the unique part later, when we try to mutate the tensor, because really the difference between tensor and `UOp` is that we can mutate tensor and not `UOp`. So maybe there's a way to do this unique thing later and do it somewhere in the assign path, but I'm not too sure about this yet.

##### **Geohot** [[00:06:36](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=396)]
Yeah. I was never... I've never been happy with the solution that we have in there now for this.

##### **Chenyu** [[00:06:45](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=405)]
Yeah. Another annoying thing is that for now, if we call `Tensor.arange` on the same thing, every time it creates a different `UOp`, because the underlying `Tensor.ones` that we use to build `arange` are different. I don't believe that's intended, because if `arange` is integer, we never need gradients on that.

##### **Geohot** [[00:07:10](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=430)]
Yeah. I mean, part of the problem is like gradients. Yeah. So...

##### **Chenyu** [[00:07:22](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=442)]
So there are two things. One is gradient and another is assign. Anyway, I'll find a way to do this. That's really the blocker. And after `arange` is moved, I believe the majority of the methods can be moved as well. There are some things I just copied into mixins. For `cumsum`, we have a two-stage `cumsum` using some helper function, so I just copied that. Another thing is `pad`. `pad` is annoying because `Tensor.pad` supports like five different modes. So for now, the one in mixins is the simplest one, basically just calling `ops.pad` on the `UOp`.

##### **Qazalin** [[00:08:18](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=498)]
Yeah.

##### **Chenyu** [[00:08:18](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=498)]
Then there's a helper function in `OpMixin` that supports const padding. Basically it rewrites into a `where` and an `add`. Most of the time we use this as a helper, so I find it much easier to just add that as a helper in the mixin. Then all the other fancy `pad` stuff for now is kept in tensor. Later we can also move that to the mixin, but those are really the leaf ones. Most of the ones that call `item` or access the underlying buffer are not going to move yet. Do we want something like that? Do we want `uop.item`?

##### **Geohot** [[00:09:08](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=548)]
No, no, definitely not. No.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=550)]
That's another thing that, yeah. So only tensors can resolve anything.

##### **Chenyu** [[00:09:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=557)]
Yeah. So the issue is we also have some other functions that use the item and use its value to do things.

##### **Geohot** [[00:09:24](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=564)]
Well, that's a much bigger problem.

##### **Chenyu** [[00:09:27](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=567)]
No, I mean, there are some like frontend API that just use that. And I don't think moving that into mixing is a good idea. So those would also be kept into the tensor.

##### **Geohot** [[00:09:36](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=576)]
Yeah. Anything that involves scheduling is kept in tensor. Yeah.

##### **Qazalin** [[00:09:41](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=581)]
Okay.

##### **Geohot** [[00:09:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=583)]
I'm not even like, where did all the code go? I see mixins is only like 700 lines, and yet tensor is only like 1200.

##### **Chenyu** [[00:09:50](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=590)]
Oh, there are like five different mixin files. Are you counting them all?

##### **Geohot** [[00:09:56](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=596)]
It says the whole directory and the six mixin files is 700 lines.

##### **Chenyu** [[00:10:04](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=604)]
Okay. We also probably only lowered tensor by 500. It still has like 2000-something.

##### **Geohot** [[00:10:12](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=612)]
Yeah, I guess. I like the dot.

##### **Chenyu** [[00:10:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=616)]
I tried very hard to keep the div minimal. The issue is tensor was very compressed. So every time when you, for example, when you try to, because now it needs to, it cannot, some of the convenient methods build on top of like tensor only calling things from tensor. And there's like some decompressor. So it's not going to be able to do that. I think it's going to be a little bit more complex from that. Overall, it's like net neutral, I hope.

##### **Geohot** [[00:10:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=647)]
So, I mean, it feels like a win. Yeah. I mean, this is a great, this is a great effort. I think the mixins are super clean.

##### **Nimlgen** [[00:11:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=660)]
Yeah.

##### **Chenyu** [[00:11:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=660)]
Okay. Anyway, I'll post if I encounter anything that I'm not too sure about. I think short term, `arange` and anything that depends on indexing are the only blockers. Another slightly annoying thing is `diff`; I will fix that separately. `pad` can keep the same API. `diff` is slightly different. We kind of want the `UOp` version to be the simplest one, but there's another variant I really want to keep, and it's kind of hard. If everything created by the `UOp` uses the same method, then the `UOp` method should match that, but sometimes that's just not true.

##### **Nimlgen** [[00:11:58](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=718)]
Can you fix size?

##### **Geohot** [[00:12:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=720)]
Say that again?

##### **Geohot** [[00:12:02](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=722)]
Size. Size is different on tensor and Uop. The tensor one is correct.

##### **Chenyu** [[00:12:09](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=729)]
Oh, okay. So, sure. Oh yeah. I check this. I just don't know what this max shape and max shard shape was for, but sure.

##### **Geohot** [[00:12:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=740)]
Yeah. So, I mean, shard shape is just the shape of the shard. If you're on a multi. And then the max of that is if it's a symbolic shape, it does vmax.

##### **Chenyu** [[00:12:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=752)]
Yeah.

##### **Chrism** [[00:12:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=752)]
That makes sense.

##### **Chenyu** [[00:12:34](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=754)]
That'd be fine. Okay. I will see the color of this. So, previously we have like Uop dot prod and sum. I just rename those to like U prod and U sum so that it doesn't conflict with the mixing one.

##### **Geohot** [[00:12:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=769)]
Something like that. Yeah. I mean, it'd be nice to see what we can clean up in `ops.py` too. Like what if that could move to mixins? What if this is just trash?

##### **Nimlgen** [[00:13:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=780)]
Yeah, sure. Okay.

##### **Qazalin** [[00:13:05](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=785)]
Yeah. Yeah.

##### **Nimlgen** [[00:13:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=787)]
So, I think that's pretty much it. Yep. That's pretty much it.

##### **Chenyu** [[00:13:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=795)]
Next, George's stuff. We just put there LLM app and new USB driver. I was summarizing what happened last week and I put these as items.

##### **Geohot** [[00:13:30](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=810)]
Yeah, yeah, yeah. The USB driver is done. I'm very happy with it. Again, it was one of those things. It was kind of like the `UPat` compiler. It's like, eh, you know, it's kind of a side quest, but the firmware is really good now. I was just fixing emulator bugs, and it's super easy. We have the TinyBox here in Hong Kong, and I have an RDNA 3 GPU on USB 3, and I just put `DEV=USB+AMD` to do all the RDNA 3 hardware tests. You don't even really have to think about it. I felt like with the old USB, it was something that you always had to think about. It was hacked, the firmware could get in who knows what kind of state. But yeah, all that's just fixed. The firmware is so simple. You just spend days figuring out the one register that you had to set, because some of the registers are documented, but it works pretty well.

##### **Geohot** [[00:14:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=869)]
It's very clean API compared to the old one. Have you tested it? Tested on Comma 4?

##### **Nimlgen** [[00:14:39](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=879)]
Uh, no.

##### **Wozeparrot** [[00:14:42](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=882)]
It's been very unstable.

##### **Geohot** [[00:14:44](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=884)]
Really? I don't have a Comma 4. I have a Comma 3X I can try it.

##### **Wozeparrot** [[00:14:48](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=888)]
What do you mean? What's unstable? So at least we have a couple of Chestnuts here that on the old firmware will at least show up over USB. On the new firmware, `dmesg` will just print `cable is bad`.

##### **Geohot** [[00:15:04](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=904)]
Oh, that's probably a pretty easy fix. I mean, the firmware is very readable. If you just throw `GPT-5.4` at it and say, like, fix the USB bring

##### **Geohot** [[00:15:21](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=921)]
up on this thing and I bet it'll do it. Yeah.

##### **Wozeparrot** [[00:15:27](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=927)]
But overall the, it just seems worse on Comma 4s. It's also unclear if this is a Comma 4 issue.

##### **Geohot** [[00:15:35](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=935)]
Yeah. I don't know. I have three computers I've plugged it into. It all works way better. I'll try it on the, I'll try it on the Comma 3X.

##### **Wozeparrot** [[00:15:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=947)]
I don't think we've noticed this on 3X. This seems, yeah, we haven't really tested 3X.

##### **Geohot** [[00:15:54](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=954)]
Yeah. I mean, so the whole, like the USB enumeration path is all, is all written in the firmware. Um, and there's a lot of like registers you can set and PHYs and timings and.

##### **Chrism** [[00:16:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=967)]
Yeah.

##### **Geohot** [[00:16:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=967)]
Yeah.

##### **Chrism** [[00:16:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=967)]
Sometimes it's been coming up at USB 2 speeds. Sometimes it just doesn't come up. Yeah.

##### **Geohot** [[00:16:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=974)]
I mean, I don't have a Comma 4.

##### **Geohot** [[00:16:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=976)]
I don't know what you want me to do.

##### **Geohot** [[00:16:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=977)]
Yeah.

##### **Nimlgen** [[00:16:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=977)]
Yeah.

##### **Geohot** [[00:16:18](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=978)]
But like you can read the firmware. It's very readable.

##### **Geohot** [[00:16:22](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=982)]
Yeah. Uh, yeah. Or Rovi can look into this. I mean, like, I don't know, like I also don't really have the kind of stuff to like look into that. Yeah. It's a way to probably, like, do you have a USB 3 analyzer?

##### **Wozeparrot** [[00:16:34](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=994)]
No.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=997)]
I mean, Comma can buy one of those. Spend a couple thousand dollars and buy like a professional USB 3 packet analyzer.

##### **Geohot** [[00:16:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1009)]
Yeah. Um, yeah. And then like, see what's going on.

##### **Geohot** [[00:16:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1013)]
I mean, I also don't really even know what `cable is bad` means. Oh, you know what it might be? Maybe it needs to PD-negotiate.

##### **Wozeparrot** [[00:17:10](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1030)]
We were wondering if it was that. So if we plug it into specific hubs, like USB C hubs, it'll work. Oh yeah. That's probably PD. Yeah. It might be PD.

##### **Chrism** [[00:17:23](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1043)]
Yeah. Because also with a USB-A to USB-C cable, you're not going to get any PD if you do that, and that seemed to be more consistent.

##### **Geohot** [[00:17:31](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1051)]
Interesting. Yeah. I mean, there are a lot of hacks. You're still using the Qualcomm Comma kernel too.

##### **Chrism** [[00:17:41](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1061)]
Yeah. Yeah.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1063)]
There's a bunch of patches to the USB in there too.

##### **Chrism** [[00:17:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1067)]
Uh, do we know if they're like mainline projects as USB working now? Okay.

##### **Geohot** [[00:17:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1073)]
Yeah, I mean, the firmware does nothing for PD, and I'm not sure if it's advertising as PD. I have a lot of the PD stuff reverse-engineered. The problem is it's very hard for me to test, because the emulator, the FTDI, and the device brown out when it PD-negotiates, and then my emulator breaks. So yeah, that's another thing that'll be fixed in San Diego. But I don't think it's a bug in the firmware.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1109)]
Yeah.

##### **Geohot** [[00:18:31](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1111)]
Like I'm going to get PD sounds like the most likely thing, especially if you say hubs fix it.

##### **Wozeparrot** [[00:18:38](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1118)]
Some hubs fix it, but it's also not consistent through a hub either.

##### **Geohot** [[00:18:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1123)]
What do you mean by consistent? Like what doesn't work?

##### **Wozeparrot** [[00:18:45](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1125)]
Like sometimes you plug it in and it doesn't show up and then other times you plug it in or you change how you plug it in and it'll work.

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1132)]
I mean, I've seen that too. All the chestnuts I have here can only be plugged into one orientation.

##### **Chrism** [[00:18:59](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1139)]
Interesting.

##### **Nimlgen** [[00:18:59](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1139)]
Okay.

##### **Geohot** [[00:19:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1140)]
I didn't know. I mean, no one else has mentioned this at Comma, but I guess it must be an issue. Maybe the stock firmware fixes this. Maybe there's some bit I need to set to detect when it's flipped.

##### **Chrism** [[00:19:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1155)]
Yeah. Yeah. I don't know how much of the driving on old firmware.

##### **Geohot** [[00:19:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1160)]
Yes.

##### **Chrism** [[00:19:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1160)]
Yes.

##### **Geohot** [[00:19:21](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1161)]
So have you run my emulator at all? No, not yet. Okay. So go in the custom firmware repo and there's a full thing in the `Claude.md`, and it tells you how to run it. It's a complete emulator that will run the firmware on the computer and emulate all the MMIO writes. Then it outputs this trace file. So what you can do is, if it's enumerating on stock firmware, install the emulator, see if it'll enumerate on the emulator. If it does, take that trace file, put that trace file in Codex, and say, hey, this one enumerates, this one doesn't, fix it.

##### **Geohot** [[00:20:05](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1205)]
I know. I see.

##### **Geohot** [[00:20:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1207)]
Yeah. So that was kind of my process for developing all this stuff. I fixed some `PCIe` instability doing this. The RDNA 4 has better `PCIe` than the RDNA 3. The RDNA 3 was just tolerant of a lot more crap. So there were all these five tuning registers. I just enumerated the RDNA 3 on the stock firmware, dumped the thing, and there's this whole page of tuning registers you have to set.

##### **Geohot** [[00:20:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1232)]
And I just. Oh, I see, I see. I kind of put it in.

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1237)]
That would be awesome. We'll try that. Get the emulator working though, it's it's really easy. Like, like the emulators in a really good state.

##### **Geohot** [[00:20:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1246)]
Well, yeah. Check it out.

##### **Geohot** [[00:20:50](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1250)]
I got that emulator working so well that it could emulate a real NVMe drive brought up by the kernel. You could put an NVMe drive in the PCIe port of the Chestnut and then plug that into a computer, and then it shows up as `sda`, like `/dev/sda`.

##### **Nimlgen** [[00:21:12](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1272)]
that was the only way i figured out the dma so

##### **Chenyu** [[00:21:23](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1283)]
Oh, you also mentioned somewhere about codegen, `rangeify`, something?

##### **Geohot** [[00:21:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1292)]
Oh yeah, okay, so I got `Qwen 3.5` merged into the LLM app. There's two things I'm not happy with about it, but it's not `B1TG`'s fault. It's putting all the state in a single tensor, but there's really two states in the gated delta net. But if you try to do `AFTER` with two `STORE`s, this doesn't work. If you have an `AFTER` op and you want to put two stores there, this doesn't work because the ranges are being created on the `AFTER`, not on the `STORE`, which isn't right. Now that we've gotten rid of assign, some of the assigned things became `STORE` and some of the assigned things became `AFTER`, and `rangeify` is making a big assumption now that the `AFTER` is on the same buffer as the `STORE`.

##### **Geohot** [[00:22:42](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1362)]
say that again um okay so like you have this construction you have this construction of like

##### **Geohot** [[00:22:50](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1370)]
Yeah, okay. So it's kind of broken, but then I realized that I kind of just don't really understand the `rangeify` code. I think a lot of it is just kind of crap that's in there for who knows what kind of reason. It's really slow, and it doesn't have to be slow. You can basically, at every `STORE`/`AFTER`, kind of read it as a new `rangeify`. `rangeify` is just kind of wrong once you have assign, once you have `STORE` and `AFTER`. So yeah, I have to think about what the right way to do that is. I kind of just want to write the slow `rangeify`, clean it up, and then we can think about making it fast again. Indexing is small, but I don't really know what `rangeify` does. Yeah, I deleted it. But yeah, the LLM app is looking pretty good and usable now. You should try it. Let's see if it came up. Is my Minimax server working? I had...

##### **Geohot** [[00:24:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1468)]
I had `GLM 5.1` add support for Minimax. Does it work? Yeah, I think so.

##### **Nimlgen** [[00:24:40](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1480)]
is it fast i'm about to find out just finished beam searching

##### **Chenyu** [[00:24:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1489)]
Yeah, I remember last time I tried, after certain contexts they became really slow.

##### **Geohot** [[00:24:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1495)]
Um, I mean, we should do like whole tests. Oh wow, 34 tokens a second, Minimax. Okay. Oh, and I asked it what model it is and it said, "I'm Floyd Code, an AI assistant."

##### **Qazalin** [[00:25:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1516)]
Great. Everything is glow code.

##### **Geohot** [[00:25:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1529)]
So it doesn't fit on a small GPU. But yeah, I didn't get around to doing the multi.

##### **Geohot** [[00:25:40](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1540)]
Got to do it a little carefully, how it supports sharding the GGUF files. But yeah, this sprint I want to add support for GLM.

##### **Geohot** [[00:25:52](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1552)]
Can we move `DTYPE.VAC`? Oh, `DTYPE.VAC`.

##### **Geohot** [[00:25:57](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1557)]
Okay, so `DTYPE.VAC` is a whole other thing. Before I do `DTYPE.VAC`...

##### **Geohot** [[00:26:05](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1565)]
No, you may just go. Oh.

##### **Geohot** [[00:26:08](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1568)]
Yeah, OK.

##### **Geohot** [[00:26:09](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1569)]
All right. Yeah. Oh.

##### **Chenyu** [[00:26:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1574)]
I can't really think about it. We can move on.

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1577)]
Well, it's either `DTYPE.VAC` or `rangeify`. I like these LLM things because you make progress on something and it does something. Maybe it's actually useful.

##### **Chenyu** [[00:26:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1588)]
Yeah. Using the library is easier than refactoring the library.

##### **Geohot** [[00:26:33](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1593)]
Yeah, yeah, yeah, yeah.

##### **Geohot** [[00:26:37](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1597)]
Okay, anyway. No, no. Okay, I'll work on `DTYPE.VAC`.

##### **Nimlgen** [[00:26:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1603)]
OK.

##### **Chenyu** [[00:26:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1606)]
Next is for Viz.

##### **Geohot** [[00:26:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1607)]
And `rangeify`. `DTYPE.VAC` and `rangeify`.

##### **Chenyu** [[00:26:50](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1610)]
Great.

##### **Nimlgen** [[00:26:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1613)]
OK, Viz is next.

##### **Qazalin** [[00:26:58](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1618)]
OK, so we've got speed upgrades. Both the server and the UI are faster to render. It came from just looking at `LLaMA` and realizing some `O(n^2)` behavior that's gone now. The `LLaMA` iteration cycle time is 2 minutes and 30 seconds

##### **Geohot** [[00:27:23](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1643)]
in master.

##### **Nimlgen** [[00:27:24](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1644)]
Great.

##### **Geohot** [[00:27:25](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1645)]
3x better.

##### **Qazalin** [[00:27:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1648)]
Yeah.

##### **Geohot** [[00:27:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1649)]
So we're going to go ahead and do the kernel analysis. Yeah, I like the kernel analysis too.

##### **Nimlgen** [[00:27:37](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1657)]
Oh, the ChatGPT one? Yeah.

##### **Qazalin** [[00:27:41](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1661)]
It's, they're still like, we don't really know where the kernels come from.

##### **Nimlgen** [[00:27:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1669)]
It's like you have to look at the source code, and you have to trace it back to the Python, but I think LLMs are pretty good at that. It just uses the CLI and figures it out.

##### **Geohot** [[00:28:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1687)]
I mean, are we not just pasting `DEBUG=4` into the LLM?

##### **Nimlgen** [[00:28:18](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1698)]
It's pretty much the same thing, yeah.

##### **Geohot** [[00:28:21](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1701)]
Yeah.

##### **Qazalin** [[00:28:21](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1701)]
Like, what does this mean afterwards? The replay of the debug graph after? Yeah, exactly.

##### **Geohot** [[00:28:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1706)]
Well, I mean, it would be kind of interesting if it was like a way to take the pickle file and just reconstruct the debug from it.

##### **Qazalin** [[00:28:35](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1715)]
Yeah, that's very easy.

##### **Geohot** [[00:28:38](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1718)]
Yeah, and that's what I would imagine.

##### **Geohot** [[00:28:40](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1720)]
Like, because right now you're saying that it takes like 1.2 seconds to bring up the thing and this is slow. But the solution here is probably not to reduce time on the call to `viz CLI`. The solution here is probably to just make fewer calls to `viz CLI`.

##### **Nimlgen** [[00:29:06](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1746)]
Like, yeah, you just have something

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1747)]
that can take in the pickle file and output the whole, output all the kernel source.

##### **Qazalin** [[00:29:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1754)]
Put it in a cached text file, whatever,

##### **Nimlgen** [[00:29:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1756)]
and the LLMs are very good at that.

##### **Geohot** [[00:29:19](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1759)]
Yeah.

##### **Qazalin** [[00:29:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1766)]
So for the agentic loop, I have basically: Codex wrote a HIP kernel for FP8A quantize. That was the slowest kernel in `LLaMA`. It's around one and a half times faster than Beam, up to 2x faster than Beam, because it's doing the DMA trick from loading directly from globals to LDS without going through registers, doing stuff like that. The code is not clean, but it works, and it's faster than what it was in master.

##### **Geohot** [[00:30:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1807)]
Yeah. I mean, I like, who did all the movement of everything

##### **Geohot** [[00:30:09](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1809)]
to the flat `LLaMA`? The flat?

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1813)]
I was bad.

##### **Geohot** [[00:30:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1815)]
Yeah. I'm happy with that. I'm happy that that stuff's out of Tensor.

##### **Geohot** [[00:30:19](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1819)]
I guess that's another reason Tensor got smaller.

##### **Qazalin** [[00:30:25](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1825)]
Yeah. One can just plug in a Tensor custom kernel. They struggle a little bit with gradients and multi. You have to really push them to do them right. But the main kernel they do as well on their own.

##### **Geohot** [[00:30:39](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1839)]
Yeah. Can you get small repros of things that are creating stupid copy kernels?

##### **Nimlgen** [[00:30:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1849)]
I'll try. Yeah. Cool.

##### **Geohot** [[00:30:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1853)]
Yeah. I mean, I think this project can definitely continue. Just improving our tooling and getting this.

##### **Geohot** [[00:31:01](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1861)]
We need to match AMD's time. We're spending. Oh, we're three hours now. How'd you do that?

##### **Wozeparrot** [[00:31:11](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1871)]
Yes, I did a bunch of changes. Nice. So FP8 native was a bit of a change. I added this `all_reduce_cast` thing that does the all-reduce in the pre-cast dtype. So when you do `sum`, it casts up to float and then does the all-reduce in float rather than doing it in `bfloat16`.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1896)]
So it's about double speed there. You fixed that. You put the all-reduce in `bfloat16` instead of float. Yeah. And then FP8 native saved a little bit.

##### **Wozeparrot** [[00:31:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1915)]
And now we also only do the abs max for the FP8 scaling. It is done locally per GPU rather than doing an all-reduce for the max.

##### **Qazalin** [[00:32:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1927)]
Great.

##### **Geohot** [[00:32:11](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1931)]
Yeah.

##### **Geohot** [[00:32:12](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1932)]
So let's finish up this. I mean, I think this is the right idea. Let's keep working on. What sort of tooling will help you continue to push this below two hours?

##### **Nimlgen** [[00:32:31](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1951)]
Good question.

##### **Wozeparrot** [[00:32:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1952)]
There's some annoying stuff. So I spent a lot of time today trying to track down where `NaN` was coming from. This is kind of the biggest thing. Especially with the small-dtype stuff, I would make a change and then the model would start NaNing and I would have no idea why it's NaNing. I can't easily trace down where the `NaN` is coming from. I don't know how easy this tooling is.

##### **Nimlgen** [[00:32:58](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1978)]
Can we see the contents of all of those?

##### **Chenyu** [[00:33:02](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1982)]
For the cases that you end up finding where it's coming from, where did it come from?

##### **Wozeparrot** [[00:33:09](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1989)]
So some of the cases were: I was passing `float32` into a `bfloat16` custom kernel.

##### **Geohot** [[00:33:18](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=1998)]
And that would break it.

##### **Wozeparrot** [[00:33:22](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2002)]
There was an initial weight that I quantized, but then for the master weights I didn't rescale back.

##### **Chenyu** [[00:33:35](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2015)]
How do you pass things in different dtypes to a custom kernel?

##### **Nimlgen** [[00:33:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2023)]
Seems like you can.

##### **Chenyu** [[00:33:50](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2030)]
Because that's some stuff. I mean, if it's a custom kernel, statically we can find that. We can probably assert that.

##### **Geohot** [[00:33:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2035)]
Yeah, that we can probably find.

##### **Geohot** [[00:33:57](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2037)]
Yeah, that's what I was hoping for. Have you been using the profiler loop?

##### **Nimlgen** [[00:34:02](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2042)]
I have.

##### **Geohot** [[00:34:06](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2046)]
Yeah, any suggestions to make it more usable?

##### **Wozeparrot** [[00:34:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2055)]
I think the agent handling is already pretty good. I can just give it to `Claude Code` and be like, what is slow? But I need to give `Claude Code` a lot of pointers, because it won't really use this CLI.

##### **Geohot** [[00:34:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2069)]
Yeah, you have to.

##### **Geohot** [[00:34:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2072)]
Well, can we get that out of extra?

##### **Geohot** [[00:34:36](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2076)]
Can we make that code high quality enough that we can move it to viz proper?

##### **Nimlgen** [[00:34:45](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2085)]
Yeah, sure.

##### **Geohot** [[00:34:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2086)]
Yeah, I think do that. I mean, the current readme in viz is total trash.

##### **Geohot** [[00:34:52](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2092)]
I think it's pretty good.

##### **Qazalin** [[00:34:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2093)]
Oh, I tried merging the READMEs. All LLMs fail miserably because they put `VIZ=1`.

##### **Geohot** [[00:35:05](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2105)]
Yeah. Do we have a flag?

##### **Geohot** [[00:35:13](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2113)]
Is there an environment flag or something that won't run the server if it's an LLM?

##### **Qazalin** [[00:35:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2120)]
`TTY`. Like, there's something in `sys` you can check, whether it's an interactive shell or not. But then the problem is that if you...

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2140)]
Yeah. I mean, that sounds good. Yeah, it sounds good in general when you have a non-interactive shell. But I don't think we actually want to run the server. We don't want to run the server.

##### **Qazalin** [[00:35:48](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2148)]
If you pipe something to head or something, yeah. Stuff like that, it's also non-interactive.

##### **Geohot** [[00:35:56](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2156)]
Yeah, but I mean, I think that probably all matches. I think that makes a lot of sense, right? So instead of running the server, I mean, you can use `-1` and `-2`, but you can also just say whenever you're in a non-interactive shell, don't run the server, and have it print something saying, "Oh, I didn't run the server. I'm in a non-interactive shell."

##### **Nimlgen** [[00:36:12](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2172)]
Mm-hmm. Yeah, that'll work.

##### **Geohot** [[00:36:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2176)]
Yeah, I think that's a good fix. I think the goal with this project isn't just to understand what the high end of agents can do. A lot of people, like when I posted that Minimax thing on Twitter, were like, George, we don't have AGI. You're not going to be able to one-shot that. I'm not downloading a bunch of stuff and running agentic workflows with agents. I'm getting the LLM, and I'm putting in, yo, make this fast. And if the LLM can't take yo, make this fast and do the right thing, I'm out. So yeah, I think we have to focus on not just the high-end capability with LLM, but imagine what some guy on his computer who downloads tinygrad is going to do. He's going to download tinygrad, write something, it's going to be slow, and he's going to open `Claude Code` and be like, yo, make this fast, and then figure out what it does. And if it doesn't do the right thing, we have to figure out how to put hints in the repo so that it does.

##### **Wozeparrot** [[00:37:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2236)]
We probably also want to respect no color.

##### **Chrism** [[00:37:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2240)]
Yeah. For a while, I always thought we should either respect `NO_COLOR` or, if it's a TTY, not print the ANSI color codes. I think Claude gets confused by this.

##### **Qazalin** [[00:37:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2252)]
Yeah, I can also make TTY not do that. `NO_COLOR` is respected now. That's fixed.

##### **Geohot** [[00:37:40](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2260)]
Yeah, I think just respecting no color is enough there. I want non-interactive shells to have color.

##### **Geohot** [[00:37:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2267)]
Yeah, that makes sense.

##### **Geohot** [[00:37:48](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2268)]
Right, I want to be able to, if I type it to a file, I want the color in the file. I want the color in the file when I cap the file later.

##### **Geohot** [[00:37:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2273)]
Yeah.

##### **Geohot** [[00:37:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2275)]
But yeah, sure, no color should definitely be respected. Like, globally, we should just change color to not do anything when it's no color. Like, that should be in helpers, not at some other place.

##### **Geohot** [[00:38:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2287)]
You know, I definitely don't want that to be non-interactive. It has no color. I love color.

##### **Qazalin** [[00:38:13](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2293)]
Yeah, Claude is good at putting `NO_COLOR`. But...

##### **Geohot** [[00:38:21](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2301)]
I see. I mean, some of this stuff can also be in the `viz` README. I think if it's actually in the repo, it'll read it more. I also like to avoid things like `Claude.md`, because my belief is that you should focus on whatever is good for humans. As humans, we're a lot better at empathizing with humans than we are with machines. So we should just focus on what's good for humans. And the same thing is true for humans, right? `JIT_BEAM` is bad. The reason these LLM people didn't have `JIT_BEAM` is because we don't do a good job of exposing that. We used to have this saying at Comma: if there's a button, it's bad, right? Because people are going to not press the button when you want them to, and they're going to press the button when you don't want them to.

##### **Geohot** [[00:39:08](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2348)]
So why do you give them a button?

##### **Qazalin** [[00:39:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2354)]
Yeah, the only good thing about `Claude.md` is that it's preloaded.

##### **Geohot** [[00:39:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2360)]
Yeah. I mean, I don't know. I'm okay with a two-line `Claude.md` that says,

##### **Geohot** [[00:39:25](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2365)]
read this README and read this README.

##### **Qazalin** [[00:39:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2369)]
That's good. Yeah.

##### **Geohot** [[00:39:30](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2370)]
Yeah. Focusing on continuing to improve any sort of tooling we can for `LLaMA`. Is there anything we can do about the `NaN`s? We had a flag that, you know how we have that flag to check the runtime, to compare it to CPU. Would it help if it just aborted

##### **Nimlgen** [[00:39:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2387)]
if a kernel had `NaN`s? If it printed the kernel, yes, actually.

##### **Geohot** [[00:39:57](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2397)]
Oh yeah. That'd be great. Let's do that. Let's add that feature. Oh yeah, continuing to improve the workflow for `LLaMA`.

##### **Geohot** [[00:40:12](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2412)]
I can feel the visible speed improvements too. They're great. Like I'm loading, just like rendering like MNIST and stuff. Like, great. They work.

##### **Chenyu** [[00:40:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2426)]
Okay. Since we already talked about `LLaMA`, Wasp, do you want to finish everything first?

##### **Wozeparrot** [[00:40:34](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2434)]
I mostly said most of the improvements. I wrote a fused RMS norm because it turns out you can't. I don't know if this is a function limitation or just a math limitation that to save RMS norm and not rerun it on the forward, you have to have a custom backward.

##### **Nimlgen** [[00:40:59](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2459)]
Unclear to me.

##### **Geohot** [[00:41:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2460)]
I have a small example I can look. It seems to save now when I wrote it this way.

##### **Qazalin** [[00:41:10](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2470)]
Okay.

##### **Geohot** [[00:41:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2474)]
Okay. Why did it say for three hours, 16 minutes that we're only getting 17% MFU?

##### **Wozeparrot** [[00:41:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2486)]
I think we are only getting 17%. We're getting 17. I don't know what the MFU number that people report is. Is it like BF16 MFU?

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2499)]
Is your model BF16 report? That's right.

##### **Geohot** [[00:41:42](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2502)]
We're FP8. So that's FP8 MFU?

##### **Wozeparrot** [[00:41:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2506)]
Yes.

##### **Geohot** [[00:41:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2507)]
Okay. I see. Yeah, our flash attention is not FP8.

##### **Nimlgen** [[00:41:57](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2517)]
Yeah.

##### **Geohot** [[00:41:58](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2518)]
It's kind of mixed. But yeah, if we can beat AMD, that's incredible. Can we beat them?

##### **Wozeparrot** [[00:42:09](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2529)]
I don't think they can.

##### **Qazalin** [[00:42:11](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2531)]
Okay. I don't think they can.

##### **Wozeparrot** [[00:42:11](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2531)]
I don't think they can. But then what do they do that we don't? Is their attention backward supposedly also in FP8?

##### **Nimlgen** [[00:42:22](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2542)]
I see.

##### **Geohot** [[00:42:24](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2544)]
Also that three hours, do we actually have a run at three hours or do we just have?

##### **Geohot** [[00:42:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2548)]
I'm doing one right now. All right. Cool. And we'll see.

##### **Chenyu** [[00:42:34](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2554)]
Also, I believe they have the latest logging library. That is for 6.0. We should try to run that too and make sure everything looks good, logging-wise.

##### **Wozeparrot** [[00:42:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2567)]
Yeah, at least when I did the logging stuff, I wrote it against `mlperflogging6-rc2`.

##### **Chenyu** [[00:43:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2580)]
I think I can double confirm later, but that's probably the one that we should use. Because we did it something last time and maybe they changed something in terms of the names and logging fields. Yeah, at least... Once you have the log, what I did last time was I just copied for however many times we need and run through our log checkers to make sure everything is correct.

##### **Wozeparrot** [[00:43:30](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2610)]
Yeah, at least I wrote it against the version that had all the checkers for 6.0.

##### **Geohot** [[00:43:37](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2617)]
Okay, sounds good. What's that three hour one? Can you just post quickly the profile.sh output?

##### **Geohot** [[00:43:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2629)]
Yes. I'm curious what percent we're actually on...

##### **Nimlgen** [[00:43:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2635)]
What percent is gems and what percent is...

##### **Qazalin** [[00:44:03](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2643)]
I don't know. Ah. That top one looks like `amax`.

##### **Geohot** [[00:44:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2654)]
Yes.

##### **Qazalin** [[00:44:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2656)]
I can fix that. Oh, there's my custom kernel.

##### **Geohot** [[00:44:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2660)]
Okay. I should try some custom kernel but I can't fix it. Yeah, I mean let's not go too crazy with custom kernels, only if they're clean and isolated. Um... Um...

##### **Nimlgen** [[00:44:36](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2676)]
That one needs to stay? That's not like a... That's... Like the best kernel is no kernel.

##### **Qazalin** [[00:44:42](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2682)]
...

##### **Geohot** [[00:44:48](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2688)]
Those `amax`es are required? Yeah, we have to do delayed `amax` scaling, because FP8 doesn't train. Got it.

##### **Qazalin** [[00:44:59](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2699)]
...

##### **Geohot** [[00:45:01](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2701)]
Yeah, it should be on that kernel.

##### **Qazalin** [[00:45:03](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2703)]
The other thing I noticed is that AMD uses atomics. I found the atomics very contending and racy, but if you make it two-stage, it's actually very fast. It's faster than atomics.

##### **Geohot** [[00:45:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2720)]
Oh... Oh, yeah, I see what you mean.

##### **Qazalin** [[00:45:25](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2725)]
I read AMD's code. They use some very complicated atomic thing, and there's not even like an atomic float max, so they use an int version with a cast.

##### **Geohot** [[00:45:37](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2737)]
There's definitely an atomic float add. I use it in embedding backwards.

##### **Qazalin** [[00:45:41](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2741)]
There's not a max.

##### **Geohot** [[00:45:44](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2744)]
Yeah, there might not be.

##### **Nimlgen** [[00:45:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2747)]
Yeah, there's no max. They just put a custom map of it. We just do this all in LDS. OK, looks good. Next is...

##### **Nimlgen** [[00:46:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2775)]
So the Mellanox driver was merged last week. I just added it to graph and trained CIFAR with it. So yeah, I think for bigger models I need to land the linear refactors first to make the dispatch copies faster.

##### **Geohot** [[00:46:42](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2802)]
So for the. You got CIFAR across multiple machines.

##### **Nimlgen** [[00:46:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2806)]
Yeah.

##### **Geohot** [[00:46:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2807)]
Awesome. And it's, yeah.

##### **Nimlgen** [[00:46:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2813)]
So yes, for the `ExecItem` removal refactor, I fed it beam to `UOps`, and I also have a PR. My current plan is that I'm going to land the `run_linear` PR, which actually will avoid using `ExecItem`s and all these runners in this schedule path. And then I'll need to refactor JIT and all the graphs, because they heavily use these runners and `ExecItem`s as well.

##### **Nimlgen** [[00:47:31](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2851)]
Oh, yeah. OK. So for USB, do we have anything for me to test in CI? I mean, like the custom firmware on the commas?

##### **Wozeparrot** [[00:47:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2869)]
That's what I was saying earlier, that I was trying to set one up today and it just wouldn't come up. Okay. We'll get more Chestnuts on Wednesday. Comma is just, their line is completely full with Comma 4 production right now, so we can't run Chestnut boards.

##### **Nimlgen** [[00:48:13](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2893)]
Got it.

##### **Geohot** [[00:48:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2896)]
Yeah, okay. No huge rush on that. I don't think it's blocking anything really.

##### **Nimlgen** [[00:48:23](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2903)]
Yeah, I'll also take a look into these framework machines.

##### **Nimlgen** [[00:48:31](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2911)]
I'm not sure I'm really concerned about the, I've already been looking at this, and I'm a bit concerned that, as far as I understand, like your message, that actually this issue persisted across different runs, I mean, the MMU issue.

##### **Geohot** [[00:48:51](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2931)]
No. So I get this on my computer sometimes too. Something will just break. It's reproducible. Yeah. It's reproducible in a Strix Halo, and it doesn't seem to go between runs. It seems to just be that the MMU will get corrupted for like the runner job.

##### **Nimlgen** [[00:49:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2956)]
Okay.

##### **Geohot** [[00:49:19](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2959)]
It's just that local page table. It's not like there's some global thing. OK. Yeah. I have a question. I think it might even reproduce without multiprocess. It seems like some page table corruption. I know.

##### **Nimlgen** [[00:49:51](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=2991)]
I'll just try to. OK. I'll try.

##### **Nimlgen** [[00:50:02](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3002)]
I don't know if it's some AMD feature again, like some weird store or something like that. But yeah, I'll try something.

##### **Qazalin** [[00:50:13](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3013)]
Yeah.

##### **Geohot** [[00:50:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3014)]
No, I haven't looked that much into it. I do know that when I do, I test N12 on my computer, I'll hit it maybe one in five times.

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3026)]
Yeah. And then nothing persists. If I do it again, it works.

##### **Wozeparrot** [[00:50:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3032)]
I wonder if this is worse if you have graphics stuff running. Because I was trying this on the Frameworks here with no graphics stack running, and I would hit it like one in 20 times. It happens in CI a lot though. This is what's very confusing me, because if I log into the machine and I just run the exact same command using the venv that the runner job set up, I don't hit it that often.

##### **Geohot** [[00:51:03](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3063)]
Yeah, I don't know about that.

##### **Nimlgen** [[00:51:05](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3065)]
I think you're just getting lucky.

##### **Wozeparrot** [[00:51:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3074)]
Potentially. But I did run it on both of the frameworks and I would hit it about one in 20 on both of them. I mean, as long as you can hit it one in 20, we still need to fix it.

##### **Geohot** [[00:51:25](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3085)]
Yeah. I don't know. Like, if it happens to be more common, if it's launched, it's on my desktop. I don't know. Maybe they're like, nice-ing the process or something and some kind of race condition.

##### **Nimlgen** [[00:51:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3107)]
Yeah.

##### **Nimlgen** [[00:51:48](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3108)]
I'm not sure if we can have any race condition from our runtime. My guess is the only thing we can do is supply the wrong addresses, but the kernel should just fail. I mean, wrong sizes for these buffers and all these things, but they can also validate this and they actually do validate this.

##### **Geohot** [[00:52:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3134)]
So, I mean, we don't really control these page tables.

##### **Nimlgen** [[00:52:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3140)]
I mean, okay, I'll take a look.

##### **Qazalin** [[00:52:24](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3144)]
Yeah.

##### **Geohot** [[00:52:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3146)]
I mean, maybe it's not even an MMU fault. I just know that it says MMU fault.

##### **Nimlgen** [[00:52:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3152)]
It's really also concerning that it's in the CPF, which is the prefetch thing that prefetches these PM4 packets.

##### **Nimlgen** [[00:52:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3166)]
So it's not like the actual execution.

##### **Geohot** [[00:52:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3173)]
I mean, yeah, maybe we aren't syncing the PCIe right, or some cache invalidation. It seems maybe vaguely related to the kernels that get the wrong time.

##### **Geohot** [[00:53:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3195)]
There's kernels that like do their timing incorrectly. And I wonder if it's like not clearing the cache correctly for the timestamps or something.

##### **Nimlgen** [[00:53:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3206)]
If you know any command that can reproduce the same thing, I'm not sure. Like, for instance, can you report these kernel issues? Can you post it anywhere else?

##### **Geohot** [[00:53:34](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3214)]
Yeah, I'm still not familiar with that. I used to be able to repro with `MMApeek`. I'm not sure if this is still true. Let me see. Does `mmapeek` still use `AQL`?

##### **Geohot** [[00:53:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3223)]
I remember I hacked and I made it use AQL. Yeah

##### **Qazalin** [[00:53:47](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3227)]
Okay.

##### **Nimlgen** [[00:54:03](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3243)]
I can't hit it without `AQL`, so I don't know. Cool. I'm excited to see a big training job

##### **Geohot** [[00:54:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3257)]
across two machines. Yeah, and then we should start thinking about how we can... Let's start seeing if we can do `LLaMA` across two.

##### **Geohot** [[00:54:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3268)]
Maybe we can get `LLaMA` across two for MLPerf. I guess those aren't Mellanoxes.

##### **Wozeparrot** [[00:54:37](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3277)]
AMD hasn't gone back to me yet. I poked them again Friday. I should probably send another email to them.

##### **Geohot** [[00:54:44](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3284)]
Yeah, you can email them again. I don't know. How much should we try to fix it ourselves? How much should we try to reseat it?

##### **Geohot** [[00:54:54](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3294)]
I think Igor's in town, if you want to do it. Yeah, Igor's here.

##### **Wozeparrot** [[00:54:58](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3298)]
It seems pretty complicated to reseed.

##### **Geohot** [[00:55:01](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3301)]
I mean, Igor's a smart guy.

##### **Nimlgen** [[00:55:07](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3307)]
We can see. Anything else from Nimlgen? No.

##### **Geohot** [[00:55:25](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3325)]
Great.

##### **Chenyu** [[00:55:26](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3326)]
We have covered `LLaMA` already. Next is the new `DEV`.

##### **Chrism** [[00:55:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3332)]
Yep. So yeah, I mean, the `DEV` syntax is all there. The things that need to be done with respect to that are just integration stuff. So for instance, you want to have everyone actually use the arch. I was looking into a little bit of how to get that to work with CPU today. And then also, making mock GPU an interface. I think the right way to do this is to say, okay, well, you have `mock+AMD` and `mock+USB`, and those are all separate interfaces. But yeah, hopefully we like the syntax. If there's any strong feelings about the syntax, or stuff you want to change, let me know.

##### **Chenyu** [[00:56:34](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3394)]
Is this thing documented somewhere?

##### **Chrism** [[00:56:39](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3399)]
I believe I wrote it up in docs. It's like there's a docs page called environment variables, I think. I think there's a section there. I'll double check that it has everything, but I think it's all there.

##### **Geohot** [[00:56:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3415)]
I also think we should consider better error messages for when you type it wrong.

##### **Chrism** [[00:57:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3420)]
Yeah.

##### **Geohot** [[00:57:02](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3422)]
So yeah, like when I tried the mock thing, it just says, like, no interface available. Or here's another one where the error is `list index out of range`, right? Ideally it should... yeah, you know what I'm saying.

##### **Chrism** [[00:57:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3437)]
I saw that. Yeah, I saw some guy had this `list index out of range` error also. Someone posted that in an issue. Obviously that's not a good error message.

##### **Geohot** [[00:57:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3448)]
I mean, this is also kind of related to a problem we've had for a long time, which is querying the number of GPUs that are available. So wherever `DEV` is resolved, we need some generic way. Take a look at `GPU Burn` for an example of something that needs fixing. `GPU Burn` just has an environment variable called `GPUS`, but we have to be able to say, like, AMD get available GPU count, or whatever the normal API is. Also, I don't want to have to do a bunch of abstractions for that. I want to be able to say which compiler to use in the...

##### **Chrism** [[00:58:13](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3493)]
Yeah. So I don't know. This seems like something that might change a lot with the `ExecItem` refactor, like this whole pipeline. But yeah, definitely it should be possible to put that in the graph somewhere. Right now, I believe the part where you choose the renderer is in `get_runner`.

##### **Geohot** [[00:58:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3523)]
Yeah. I don't know. Maybe this can wait for after that refactor.

##### **Geohot** [[00:58:48](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3528)]
I also saw you merge this explicit-types thing. Can you add a test to CI that tests the import speed of all the autogens?

##### **Chrism** [[00:58:56](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3536)]
Yeah. Yeah, I will do that. It's like twice as fast with that change. I mean, obviously it depends on what you're running it on. But yeah, the big thing there is that it got rid of `init records`, or whatever I called it.

##### **Geohot** [[00:59:14](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3554)]
I mean, you can't have something that's `O(n)` in something that's doing...

##### **Chrism** [[00:59:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3560)]
Yeah. It turns out the big issue there was actually evaluating all of the types. So now it doesn't do that anymore. I just put the types explicitly, and so that's a big win. That's nice and fast. The other thing with regard to ctypes is that the issue Armand had opened about it being slower is no longer the case. It's just as fast as the thing he was comparing it to, so it's no longer regressed. And apparently it's fast enough for them. So that's good. The other thing that came up was that they're having some issues moving all their models to a single `JIT`. There's an issue that you just opened, I think last night, which goes into more detail about what the issue is, but it's something to do with the memory planner. He says when he turns off the memory planner, it doesn't have this issue. But I haven't looked into it enough to know exactly what the issue is. Interestingly, he says it only happens on Qualcomm. Anyway, I have to look into this a little more.

##### **Qazalin** [[01:00:45](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3645)]
But. Cool.

##### **Nimlgen** [[01:00:56](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3656)]
That's it.

##### **Chenyu** [[01:01:00](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3660)]
So I just remembered something. Can we put whatever fastest GEMM we have for RDNA 3 on the CI benchmark?

##### **Geohot** [[01:01:15](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3675)]
Sure. You want to add?

##### **Geohot** [[01:01:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3677)]
Well, so we have `amd_copy_matmul`.

##### **Chenyu** [[01:01:20](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3680)]
I know last time when I tried it, it's not as fast. I don't know if it's because I missed a flag or something.

##### **Geohot** [[01:01:30](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3690)]
Yeah. I don't know about that, but I can look at it at this point. Yeah.

##### **Chenyu** [[01:01:35](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3695)]
Yeah, because I want to try to see how good our tooling is at writing that stuff. But I don't even know what's the fastest we have now.

##### **Geohot** [[01:01:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3706)]
I have an RDNA 4 asm one that's pretty fast too, so I think I merged the RDNA 4 asm one.

##### **Nimlgen** [[01:01:54](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3714)]
Okay. Oh, also. It has bank conflicts.

##### **Geohot** [[01:01:58](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3718)]
It has bank conflicts. I know. I know. Yeah. I've tried to fix them and.

##### **Qazalin** [[01:02:04](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3724)]
I added PMCs. I added PMCs to the CLI. Codex can look at them, right.

##### **Chrism** [[01:02:11](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3731)]
The one other thing I forgot to mention is read-only structures. So I have a PR open for this, but it's kind of dangerous because what you're basically doing is taking a read-only memoryview and turning it into a writable memoryview. So if you had a memoryview over something that was only mapped as `PROT_READ`, you can obviously cause a segfault. If you check this every time you access your fields, then you end up making your code much slower. The question is kind of like...

##### **Geohot** [[01:02:55](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3775)]
What's wrong with a segfault?

##### **Chrism** [[01:02:56](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3776)]
Fine. It would be nicer if it sort of asserted, right?

##### **Geohot** [[01:03:01](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3781)]
I don't care that much.

##### **Chrism** [[01:03:03](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3783)]
All right.

##### **Geohot** [[01:03:04](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3784)]
If you try to write to something that's read-only and it segfaults, that seems totally reasonable.

##### **Chrism** [[01:03:09](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3789)]
Okay. Fair enough. Anyway, the big question was whether or not, like, Nimlgen, you had mentioned this previously as being something useful. So if it's useful for you, then I will merge it. But otherwise it does make the memoryview logic more complicated, so I don't want to merge it if it's not useful for anything.

##### **Nimlgen** [[01:03:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3812)]
And is everything already working fine? But for readability in some places, maybe it's...

##### **Nimlgen** [[01:03:40](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3820)]
It's just for readability. Okay. I also tried to do that and I just saw that it's kind of not a one-line change.

##### **Nimlgen** [[01:03:57](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3837)]
So just... okay.

##### **Chrism** [[01:03:59](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3839)]
Yeah. Yeah. I mean, the problem is that you're doing this Python API thing where, now that you're using the Python API, that means that `to_mv`, `mv_address`, and `from_mv` can't be in `helpers.py` anymore because they import other stuff from tinygrad.

##### **Geohot** [[01:04:22](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3862)]
Yeah. So I wouldn't say that it's really important to bring this in.

##### **Nimlgen** [[01:04:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3868)]
Yeah.

##### **Chrism** [[01:04:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3869)]
Okay. Yeah. If it doesn't make a huge difference... The thing you had mentioned was that it might make USB faster, but that's not...

##### **Geohot** [[01:04:36](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3876)]
sure.

##### **Nimlgen** [[01:04:42](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3882)]
I think my implementation, just in some microbenchmarks, was faster.

##### **Nimlgen** [[01:04:46](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3886)]
I know you fixed a lot of stuff. So maybe it's already. It's fine.

##### **Chrism** [[01:04:52](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3892)]
Okay. Yeah.

##### **Nimlgen** [[01:04:54](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3894)]
Then maybe forget it. Okay.

##### **Qazalin** [[01:04:56](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3896)]
Yeah.

##### **Nimlgen** [[01:05:04](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3904)]
Oh, anything else for the meeting? Nope.

##### **Geohot** [[01:05:10](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3910)]
That's it. The users are coming, guys.

##### **Geohot** [[01:05:13](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3913)]
We got to be ready for users.

##### **Qazalin** [[01:05:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3916)]
Oh.

##### **Geohot** [[01:05:16](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3916)]
It does seem.

##### **Wozeparrot** [[01:05:19](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3919)]
Symbolic batch with Onyx.

##### **Geohot** [[01:05:21](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3921)]
Content.

##### **Nimlgen** [[01:05:25](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3925)]
Oh, Let me just.

##### **Qazalin** [[01:05:28](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3928)]
I was just about to say.

##### **Geohot** [[01:05:34](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3934)]
For which… for their Triton servers? Unclear, but they were asking about this.

##### **Nimlgen** [[01:05:45](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3945)]
For Dalek's harmonics.

##### **Geohot** [[01:05:49](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3949)]
Well, it was Mitchell asking about it, so it's probably Triton servers.

##### **Nimlgen** [[01:05:52](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3952)]
Yeah. Just ask him to open an issue or something. Has Comma updated the tinygrad version?

##### **Chenyu** [[01:06:08](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3968)]
Are they happy with the latest stuff?

##### **Chrism** [[01:06:11](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3971)]
I haven't heard any complaints. Usually they're pretty vocal when they have complaints. I will double check that they actually updated, but as far as I'm aware, they have a script.

##### **Chenyu** [[01:06:21](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3981)]
It seems to be like five days ago, so… Yeah. Sorry?

##### **Geohot** [[01:06:27](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3987)]
It was updated five days ago.

##### **Chrism** [[01:06:29](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=3989)]
Oh, okay. Great. Yeah. No, they have a script that runs every week and automatically updates their dependencies. And as far as I understand, we should be always updated.

##### **Nimlgen** [[01:06:42](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4002)]
Cool. Okay. We're getting users. Great. We will probably do a release sometime soon.

##### **Geohot** [[01:07:09](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4029)]
We should also think about our dependency on the internet. Like right now we're pulling headers down from the internet.

##### **Geohot** [[01:07:17](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4037)]
We probably shouldn't be doing that.

##### **Qazalin** [[01:07:19](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4039)]
Yeah.

##### **Nimlgen** [[01:07:24](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4044)]
I mean, it's pretty annoying because these files are really, really big. I think we need to strip them somehow.

##### **Geohot** [[01:07:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4052)]
Yeah.

##### **Nimlgen** [[01:07:32](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4052)]
Before…

##### **Geohot** [[01:07:35](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4055)]
I don't know. This is just something that has to happen before the next release, I'd like to think about. But otherwise…

##### **Nimlgen** [[01:07:43](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4063)]
Cool. Okay.

##### **Chenyu** [[01:07:45](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4065)]
I think that's it for this meeting. Thank you, everyone. See you next week. Thanks. Bye-bye.

##### **Nimlgen** [[01:07:51](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4071)]
Bye. Bye-bye.

##### **Qazalin** [[01:07:53](https://www.youtube.com/watch?v=l2GRAx-2V-M&t=4073)]
Bye-bye.
