# 2026-01-12 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time (reversed order today)
- company update
- image dtype
- drivers
- viz / fast gemm
- llama flash attention
- jit asserts, schedule
- assembly
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=MLaBoY1Hb9U)

### Highlights

* **[Company update: long-horizon chip competition](#geohot-000004)**: Notes that building an AI-training stack means effectively competing with NVIDIA and Google (the only two “successful at building chips to train AI”), and that it will take a long time.
* **[Unifying scheduling/allocations across the stack](#geohot-000217)**: Reasserts that instruction scheduling, kernel scheduling, register allocation, and memory allocation are fundamentally the same problem at different scales—and argues the first step is a unified framework (not split across LLVM vs. framework-specific allocators).
* **[Type-checking focus: add MyPy failure tests](#geohot-000545)**: Suggests adding tests that explicitly assert MyPy behavior (designed “MyPy failing tests”) to keep typing changes honest.
* **[Qualcomm perf counters + improved C types](#chrism-000354)**: Chrism is enabling Qualcomm performance counters to debug why `IMAGE=1` is slow, and finishing new C-type annotations to improve editor IntelliSense (with MyPy understanding it better than Pylance so far).
* **[2D image handling: late rewrite near valid-masking](#geohot-000639)**: Advises implementing 2D image support as a late rewrite at the same stage as current valid-masking, converting indices to 2D and extracting 2D coords only when passing into texture sampling.
* **[AMD: “noise time copy” merged, decoder speed up](#nimlgen-001100)**: Reports the AMD “noise time copy” is merged; VCN decoder speed is “1580 frames/s” at `beam=1`.
* **[MI350 all-to-all bandwidth gap + contiguous copy overhead](#nimlgen-001125)**: Says MI350 all-to-all is ~150 GB/s vs. a ~220 GB/s target; suspects extra contiguous-related copies and suggests using views to avoid copies.
* **[Remote/shim direction: reuse the abstraction layer](#geohot-001722)**: Discusses using the existing memory-access abstraction (used for USB) as the foundation for remote access and a “shim binary,” envisioning racks of GPUs controlled by a simple host.
* **[Viz upgrade: register dependency highlighting](#qazalin-001912)**: Viz can now highlight all producers/consumers of a selected register (parsing register pairs), making low-level GEMM work easier when register semantics aren’t obvious.
* **[Sprint priority: integrate fast GEMM for llama training](#geohot-002049)**: Pushes that getting a fast GEMM (CDNA path) integrated for the llama trainer is a top priority, even if it requires refactoring.
* **[Llama flash-attn debugging: JIT-only incorrect V kernel](#wozeparrot-002916)**: Wozeparrot reports a strange issue: after splitting QKV backward into three kernels, only the V kernel produces incorrect outputs during JIT (despite similar computation to K).
* **[JIT edge cases: const tensors + list/tuple inputs](#chenyu-003021)**: Chenyu adds tests and notes a failure mode when passing a const tensor (can’t be realized to contiguous, and JIT doesn’t capture it), and that JIT now supports list/tuple inputs—but the “spec” for nesting/custom objects isn’t defined.
* **[JIT improvements idea: multi-shape contexts + free intermediates](#geohot-003510)**: Proposes (1) multiple JIT contexts keyed by input sizes (e.g., varying batch sizes), and (2) making intermediate memory a slab that can be freed/reallocated each call cheaply (hitting LRU most of the time) to enable multiple contexts safely.
* **[Debugging principle: design tooling for humans, not AI](#geohot-003958)**: Argues debug output and tools should be made human-readable first (what helps humans will help models), calling out confusing debug levels like “debug=3.”
* **[Claude limitations: hardware model from tests didn’t work](#geohot-004508)**: Says he tried having Claude write a hardware model to match cycle-accurate emulator tests and “burned hours”—it couldn’t do it reliably.
* **[Assembly toolchain status: PDF/DSL/SQTT cleaned up](#geohot-004532)**: Reports major cleanup of the PDF auto-generator and the Python DSL for AMD assembly; SQTT compare tests match RocProf TraceDecoder; aims to move PDF/DSL into core tinygrad soon and build a full AMD assembly environment.
* **[Perf note: cleaned-up matmul gained ~10%](#geohot-004852)**: Mentions taking an AMD matmul (from a blog-post baseline) and getting an additional ~10% speedup, reaching ~50 TFLOPS after cleanup.
* **[Roadmap: “year of LLVM removal” + SASS/DSP targets](#geohot-004959)**: States a goal to remove LLVM dependency over 2026, add backends like NVIDIA SASS and DSP output, and sets a 2027 horizon for being “ready to write our hardware.”
* **[FP8 merged; birds training bottlenecks on flash-attn](#chenyu-005127)**: Chenyu merged FP8 (linears use FP8 and are faster), but training birds is now bottlenecked by flash attention, making further GEMM gains harder to see on small models.
* **[Flash-attn NaNs: likely a real bug, not “bird is small”](#geohot-005202)**: Pushes back on the “bird is too small” explanation; suspects a correctness bug (especially in backward / max handling) as the likely cause of NaNs.
* **[Reproducibility: seed added to BERT data server](#b1tg-005402)**: B1tg added a seed so runs can be compared; confirms identical loss and accuracy with the same seed.
* **[Clamp behavior: now matches torch, but slower](#b1tg-005530)**: Notes clamp backward behavior now matches Torch but slows a kernel; suggests it could be sped up (e.g., simpler min/max), while maintainers prefer matching numerics for now.
* **[Bounties: overwhelmed by low-validation AI submissions](#geohot-005737)**: Says bounties became hard because many submissions are “casually” AI-generated; the real value is in validation/review effort, not volume.
* **[PR guidance: split into smaller, useful pieces](#chenyu-005808)**: Advises contributors to split large PRs into independently valuable chunks to reduce maintainer review load; large (~500-line) PRs with unclear benefit tend to get skipped.
* **[Next meeting time discussion](#chenyu-005913)**: Says they’ll discuss shifting the meeting time next week (likely same time or one hour earlier).

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=0)]
So let's start with company updates.

##### **Geohot** [[00:00:04](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=4)]
So first off, I'm in Asia right now, and it is one in the morning. So I don't know if we move the meeting next week. We should really find a time that works for everybody. I just posted the market cap thing, you know. I know it just feels like everything takes so long. It feels like all of Tinygrad takes so long, and there are so many pieces, and like, oh, why are you writing a DSL for assembly language? Just always remember that the biggest two companies in the world are both the only two companies that are successful at building chips to train AI. The biggest company in the world is NVIDIA, and the second biggest company in the world is Google, and they're the only companies with AI training chips. And it's just kind of interesting. It's interesting to notice that. So then, like, when you think about Tinygrad in perspective, like, does anyone have a better way to do this? Is there anybody out there who has a better? This is just really hard. But yeah, no, I think we can succeed at it, and it's just going to take a really long time. But, you know, if you don't think that competing with, I mean, at the end of this really long time, it's going to take a really long time. You end up competing with the actual two largest companies in the world.

##### **Geohot** [[00:01:33](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=93)]
So something to think about. You don't like Cranium?

##### **Geohot** [[00:01:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=107)]
I mean, it's also interesting that almost every other one of those companies on that list has tried to build a training example.

##### **Geohot** [[00:02:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=120)]
So, you know, I think it's going to take a really long time. Except for Saudi Aramco. TSMC. Well, TSMC builds. TSMC makes, it's crazy.

##### **Geohot** [[00:02:17](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=137)]
I mean, just look at those are the biggest companies in the world. But we'll get there. But, you know, it's going to take a really long time. And I'll. I'll. I'll reassert the tiny grab thing over and over, which is that all of these things, instruction scheduling, kernel scheduling, register allocation, memory allocation, they're all the exact same

##### **Geohot** [[00:02:41](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=161)]
problem, just at different scales. And the first step to unifying them is to bring them into a unified framework.

##### **Geohot** [[00:02:54](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=174)]
But there's no way that if register allocation is being done in LLV, you're going to have a lot of things that are going to be in the same place. And there's no way that that's going to use the same logic as the torch memory allocator, which is done in torch. But you have to use the same logic. You just want to build one really good one. You don't want to keep rebuilding stuff over again. It's also notable that. Neither Nvidia nor Google uses LLVM. Whether LLVM is capable of.

##### **Geohot** [[00:03:26](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=206)]
Training big models is another question. Open question.

##### **Chenyu** [[00:03:39](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=219)]
I know I reversed the order, but seems it's late for you, George. You want to finish your assembly stuff first?

##### **Geohot** [[00:03:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=227)]
And also, let's go with that order.

##### **Chenyu** [[00:03:51](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=231)]
For then, let's start with Chris.

##### **Chrism** [[00:03:54](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=234)]
Yeah. Yeah. So I started working on. Getting the performance counters to work for Qualcomm. I think that'll really help out. Trying to understand what is keeping image equals one slow. So that's a good thing to work on. And then the other thing, unless there's stuff to talk about with respect to that. Is C types. Which is coming along. There's a couple of things I need to only document. I iron out, but that should be done today. The new C type stuff. It's the Intellisense stuff is better. I checked it out. It's not perfect. But it is better than it was what it was previously. Which is that it didn't work at all. And now it works sort of. I don't know. I don't know exactly know how Pylance works. So I'll have to take a look at this and try and figure out exactly what's going on here. That's causing it to not like show the actual types properly. But like sometimes the functions don't properly show the types. And I'm not totally sure why that is. But I will. It should be. It should definitely be doable. I just don't. I don't really. I'm not familiar with Pylance enough to know why this is not working yet.

##### **Geohot** [[00:05:12](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=312)]
Oh, I mean, there's Pylance and then there's MyPy. MyPy is where I'd really like it to work. I never found Pylance to be that. I mean, I guess it is nice to have it like light up in the editor. If that's what you mean by Pylance.

##### **Chrism** [[00:05:24](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=324)]
Yeah, that's what I mean. Is. Like when you mouse over in VS code, like you mouse over a function, it should show you the types of arguments of the function and what it returns. And for some reason it's not doing that. But MyPy seems to understand it properly. I've got to double check that this is the case, but I. MyPy seems to understand what I'm writing down.

##### **Geohot** [[00:05:45](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=345)]
Yeah, we should probably have some tests that like assert. Like designed MyPy failing tests.

##### **Chrism** [[00:05:53](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=353)]
Yeah, yeah, yeah, yeah. I'll look into that. That's that's a. See how easy that is to write and I test. But it should be good.

##### **Chenyu** [[00:06:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=362)]
Yeah.

##### **Chenyu** [[00:06:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=362)]
We also generate a report for MyPy. I think they have some stats for how many lines are infer as any and how many of those are properly typed. Maybe start with that.

##### **Chrism** [[00:06:15](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=375)]
Yeah, that could be good, too. Yeah.

##### **Geohot** [[00:06:18](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=378)]
Well, that's cool. Yeah, we don't need to falsify it. We can just see if the types are actually validating correctly.

##### **Geohot** [[00:06:25](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=385)]
Well, yeah, that's the generate report thing. What is something like that report something? I'm not sure. But yeah, I just look at the options.

##### **Geohot** [[00:06:39](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=399)]
Yeah. And what I'll say about the performance counters is, I mean, we know one of the major reasons for a regression, right? Like we have to support 2D images. Yeah. Yeah. Oh, for sure. So, I mean, I think performance counters are a little bit more of a challenge. I think performance counters are a good idea, but I think it's probably more important to get the known stuff first. And then once we're in the unknown, well, in the unknown, but...

##### **Chrism** [[00:07:01](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=421)]
Okay. And the advice on how to do the 2D images is just like a super late rewrite to transform the image?

##### **Geohot** [[00:07:09](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=429)]
Yeah. So you'll have to do this at the same place where we do the valid masking stuff now. Yeah. But yeah, I mean, that should be fine. Because you know it's float four by then. Yep. Yeah, just make the index 2D. And yeah, do the rewrite there. Yeah. Okay. That makes sense. Yeah. And then extract what the 2D things are at the end when you need to pass them into the texture, the sample. Yeah.

##### **Chrism** [[00:07:40](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=460)]
Yeah. Yeah. I mean, there's only... Like if you have multiple things where you're relying on this valid thing, you can only do it... You can only like perform that operation once. So you have to try. You have to try to extract that information. But...

##### **Geohot** [[00:07:53](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=473)]
Yeah. I wouldn't... Well, so is that even true? Can't you just put it in twice and give it two different sizes?

##### **Chrism** [[00:08:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=482)]
Oh. Yeah. But then you'd have to pass it to the... Yeah. You could do this. You could do this. You'd have to pass it to the thing twice. You'd have to pass it... You'd have to like make it a two function. Like the function has to accept multiple parameters.

##### **Geohot** [[00:08:16](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=496)]
Yeah. I mean, what you might want to do is you might want to, when you do the rewrite of the load, you might want to rewrite the define global as well to have the sizes. Yeah. I mean, you can keep the image D type. Just the idea is that you don't use it anywhere in the front. Yeah. Yeah, for sure.

##### **Chrism** [[00:08:35](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=515)]
Yeah. Yeah. Okay. I mean, so that's an interesting idea. To pass multiple copies of the... Like every time you want like a special valid thing, then you pass another copy of the... Of the buffer?

##### **Geohot** [[00:08:52](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=532)]
Yeah.

##### **Geohot** [[00:08:52](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=532)]
I mean, you could see if it ever happens. Yeah. But yeah, I mean, if you were to like put that type on the define global, then it would dedupe... Then it wouldn't dedupe the define globals. Then you can pass another copy of the buffer with a different... Okay.

##### **Chrism** [[00:09:10](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=550)]
Yeah. Is that okay to do that late? With that... There's no operations that have to happen on the define global before that step?

##### **Geohot** [[00:09:18](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=558)]
No. I mean, you could rewrite the define global with the image type, right?

##### **Chrism** [[00:09:22](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=562)]
Yeah. Yeah. No, I know. But I'm just worried about doing it so late in the... But I guess it's probably fine.

##### **Geohot** [[00:09:28](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=568)]
Oh, that's fine. But yeah, no, if you then were to... I understand. So basically what we're talking about here is you have two different loads that access it in two different ways, and we don't have a global like unique-ing mechanism for that. Yeah. Yeah. I mean, I would just see if you could just have it just rewrite it anyway, and then just pass it in twice.

##### **Chrism** [[00:09:48](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=588)]
Yeah. Okay. That makes sense. Yeah. Yeah. I mean, probably the quote unquote proper way to do this is to have two different samplers. It doesn't... At the end of the day, when it goes into the op skew com, it's the same thing. So it doesn't really matter.

##### **Geohot** [[00:10:01](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=601)]
Yeah. I mean, you can decide... They'll still have the same arg number on the define global. They'll still both be like zero. So maybe you can actually make it have a different sampler, but just different sampler. Oh, okay. Okay. That's... Don't change... Oh, yeah. Don't change the arg number on the define global. The thing that'll make the define global not dedup is if they have different types. You'll get all this kind of a fray.

##### **Chrism** [[00:10:23](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=623)]
Yeah. Yeah. No. The thing I was thinking was that you would pass... Because you're just installing all of these in the constants, as constants. That's where the arguments go. So I was just like, oh, well, you just install another copy of it. Yeah. But yeah.

##### **Geohot** [[00:10:35](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=635)]
It doesn't matter how you do it. Okay. Anything else? I think that's it. Yeah. Okay. That's it. Let's move onto the drivers.

##### **Nimlgen** [[00:11:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=660)]
So the noise time copy for AMD is merged. So in VD decoder speed is now fully jittered and it's 1580 frames a second with beam

##### **Geohot** [[00:11:20](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=680)]
with beam equals one. So yeah.

##### **Nimlgen** [[00:11:25](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=685)]
Yeah, I also did some, also applied some like macro optimizations for MI350, MI300. So it's a bit faster than my HDMI now. So actually all to all on MI350 is 150 gigabytes. A second. So like the target is 220. But still we have like compute kernels in front of this because of contiguous. So yeah, that's apart from that. That looks good.

##### **Geohot** [[00:12:09](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=729)]
Target is 220 or 179?

##### **Nimlgen** [[00:12:12](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=732)]
Uh, MI350 is faster. So 220 for MI350.

##### **Geohot** [[00:12:21](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=741)]
Oh, I'm sorry. So we have like 150 now.

##### **Geohot** [[00:12:23](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=743)]
What's, what's the gap? Yeah, I mean, we do have like compute kernels in front of this because of contiguous and we just copy like the data. But that should be so fast.

##### **Nimlgen** [[00:12:44](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=764)]
Um, it's not really fast.

##### **Geohot** [[00:12:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=767)]
Wait, but shouldn't it be... you you're saying it's making a copy but that should be like eight terabytes a second or so

##### **Geohot** [[00:12:56](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=776)]
yeah but no actually actually um yeah we do two copies and

##### **Nimlgen** [[00:13:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=788)]
i know but actually it takes up about like 80 us 800 us uh and like the whole copy is like six milliseconds so it's about one seventh of the whole time

##### **Geohot** [[00:13:28](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=808)]
it doesn't make sense to me because it should be like how many gigabytes per second is that continuous happening at

##### **Nimlgen** [[00:13:36](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=816)]
uh i don't have exact numbers right now but i think here around i mean several terabytes definitely i'll check that

##### **Geohot** [[00:13:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=827)]
i'm surprised that i'm surprised that it's even noticed like barely i'm surprised that it's like impacting things almost at all copies are so fast um

##### **Geohot** [[00:14:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=840)]
also why do we need the copy so we actually do copies now because of contiguous but

##### **Nimlgen** [[00:14:10](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=850)]
potentially we do not need these copies i mean we can be smart and apply some views to these uh so we can be smart and apply some views

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=858)]
cool uh yeah about uh anywhere are you looking to uh mac usb

##### **Nimlgen** [[00:14:27](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=867)]
no i'm gonna do this this week

##### **Geohot** [[00:14:32](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=872)]
yeah it seems like you're you're mostly on track with your sprint um oh i looked into i looked into idle a bit uh idle power i think that there's no uh the smu just doesn't support it

##### **Nimlgen** [[00:14:48](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=888)]
yeah actually they just keep adding like new features in the new firmware versions to disable some parts uh i know maybe this will come

##### **Geohot** [[00:14:59](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=899)]
oh it's in the new firmware version or you're hoping it'll come in a future firmware version

##### **Nimlgen** [[00:15:04](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=904)]
no i hope it will because they still adding like some things to disable some parts of the gpu like vcn and all that is still coming i mean it was recently added

##### **Geohot** [[00:15:16](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=916)]
like in november so i'm just shocked which was that what's vcn

##### **Nimlgen** [[00:15:21](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=921)]
video core next i mean oh okay like the decoders

##### **Geohot** [[00:15:29](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=929)]
the decoders or something yeah yeah

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=934)]
cool yeah no i was hoping there'd be some some uh smu shut down the memory command but i didn't see

##### **Geohot** [[00:15:42](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=942)]
it

##### **Nimlgen** [[00:15:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=947)]
yeah i know my idea was to try like d3 cold state or something like that and just restore pci

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=955)]
like state i tried that uh i tried that and i crashed the computer a few times doing it uh it does nothing you set it to d3 and the power draw doesn't change at all

##### **Geohot** [[00:16:07](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=967)]
i see

##### **Geohot** [[00:16:10](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=970)]
cool yeah i'm excited for the the shim binary i mean i think kind of the shim binary is maybe it'll almost have the same api as a remote

##### **Chrism** [[00:16:19](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=979)]
the

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=983)]
even the nice which gets to the Shi with the invisible

##### **Geohot** [[00:16:29](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=989)]
is like this is the other part that keeps doing like idiosyncrasies zal yeah i like friend it's definitely receive the same thing reasoned by z cortex though on local Yeah, I wonder if Mac USB should be the same thing. I mean, we could go a little lower level, because it is on the same computer. We probably could, like, map the region in.

##### **Nimlgen** [[00:17:07](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1027)]
Yeah, I mean, USB is, yeah, kind of the same thing. I think our obstructions are good, because we have the memory accesses all obstructed. Like, for the USB. And I think this will work fine for the remote accesses as well.

##### **Geohot** [[00:17:22](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1042)]
Agreed, yeah, no, I mean, it's awesome. We have a great extraction layer there. So I think that that's the one we should use for remote. Maybe even reuse for the shim. I mean, I'm just, I imagine racks of GPUs, if the dumbest computers possible, attached to them. And then one computer just powering up all,

##### **Geohot** [[00:17:44](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1064)]
you know, all thousand GPUs. Yeah. I have one thing to add for MI350.

##### **Chenyu** [[00:17:59](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1079)]
Last week, I trained a bird for eight stuff.

##### **Chenyu** [[00:18:04](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1084)]
But for some reason, I cannot get AMV to work. So I end up just load AMV GPU and use that.

##### **Geohot** [[00:18:11](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1091)]
The error message was not very helpful. I was not sure if it's supposed to work,

##### **Chenyu** [[00:18:18](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1098)]
or am I on, like, something that was modified midway or something.

##### **Nimlgen** [[00:18:25](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1105)]
I know. What the error message was, do you remember?

##### **Chenyu** [[00:18:29](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1109)]
I don't quite remember. One of it is, like, permission error for some file.

##### **Geohot** [[00:18:35](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1115)]
I think that's the one. I can remember. I can look it up again and let you know. But I was just not sure. I was not sure if it was supposed to work. Yes. And I think it was, yeah. Yeah, so you can... I'll try again and let you know. Yeah.

##### **Chrism** [[00:19:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1140)]
Cool.

##### **Geohot** [[00:19:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1142)]
Okay, sounds good. Uh, next for... uh, Viz or Jen.

##### **Qazalin** [[00:19:12](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1152)]
Yeah, Viz now has, uh, this feature of an E-Credit-Planet register. It highlights all the producers and consumers of that register. I use some of the infrastructure in RTSL to, like, parse the register pairs. I think it's been very helpful for my gem stuff, because most of the time I'm looking at a gem, and I don't know what that register is. I feel like I have this a lot with the gem right now, where it's so low level, that it's... um... it's becoming really hard to change anything about it.

##### **Geohot** [[00:19:51](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1191)]
Is it a CDNA gem or an RDNA gem? Uh, I mean, like, all of them are the same. Are they? Uh... Well, yeah, sort of.

##### **Geohot** [[00:20:06](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1206)]
So I think that the... I mean, they're very different, like, from like a microarchitectural perspective. I haven't looked much at that. At the CDNA. But the way that you get speed is, I think, quite different.

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1223)]
Um... But, I mean, even if we don't make it faster, how close are we to just integrating the CDNA fast gem? Present answer? Yeah. I think it will take some refactoring, but we can get there.

##### **Geohot** [[00:20:49](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1249)]
I mean, I didn't see that on your sprint goals, but I think that's pretty important. Uh... That we have... uh...

##### **Geohot** [[00:20:56](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1256)]
a fast gem being used for our llama trainer.

##### **Chrism** [[00:21:01](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1261)]
... ... ... ...

##### **Geohot** [[00:21:10](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1270)]
... ... ... ... Eternal對

##### **Qazalin** [[00:21:39](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1299)]
Bow象

##### **Chrism** [[00:21:40](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1300)]
Bow象

##### **Geohot** [[00:21:41](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1301)]
What, the LLVM stuff?

##### **Qazalin** [[00:21:45](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1305)]
No, there's a little text file that has the instructions in it.

##### **Geohot** [[00:21:51](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1311)]
Yeah, yeah. I mean, the more I think about the problem with assembly language, it's just the fact that nobody built real tooling for it. Assembly language all has syntax from the 80s. I think everybody just for some reason is fine with this because nobody actually codes assembly language. But like it has a programming language semantics of a language from like 1982. So when you say tooling for inspecting GPU state at cycle level.

##### **Geohot** [[00:22:26](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1346)]
And how's that coming? Well, I think. The current SQTT stuff.

##### **Qazalin** [[00:22:39](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1359)]
Doesn't really show a good picture of what the GPU is doing at the every cycle. I imagine like every wave at every program counter. What's going on? Where is it stalling? I agree.

##### **Geohot** [[00:22:57](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1377)]
I agree. Have you lifted the output from my SQTT stuff?

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1380)]
I think it's a lot more like clear. I think it's a lot more like clear.

##### **Geohot** [[00:23:10](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1390)]
I think it's a lot more like clear. I merged I merged it. So you're welcome to add support for already 94. But again, I think the highest priority is just getting fast gems working on birth.

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1405)]
I see. Yeah. But you know, I'll merge. I'll merge the.

##### **Geohot** [[00:23:36](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1416)]
But when I merged this, this do refactor to the DSL. I think then it should be kind of good for other people to start working on different parts of that. You're welcome to add our DNA for support to SQTT. I'm on the HP that hard. I mean, I'm not sure what it is, but. Yeah, try it on. Try it on our DNA three. And yeah, it's just it's just a lot more like clear to me because every basically every single thing that I've done. You know what I'm saying, right? 達 box is the specify, no matter the entity that it gets싸pped in. I don't need this. There's actually a dev chopsticks that imparts also running its components. And it's printable and it works from the information that comes with it. So that looks pretty cool. Ltd, that sounds cool. Yeah, they get in with buffers. That's good. Perfect, perfect. But the key thing is, you can see both. Well, what? Mike, did may. It's 612. Women are always staring at you. Oh, looks good, actually. şu. visualize where each current thing is, like the program counter of each warp.

##### **Geohot** [[00:24:38](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1478)]
I think that kind of stuff would be cool to be able to step through. Actually, if we're stepping through and we have an emulator, we should be able to see all the registers still, the values. Yeah, I was thinking like a table of all the VGPRs.

##### **Qazalin** [[00:25:06](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1506)]
Can you see them changing?

##### **Geohot** [[00:25:09](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1509)]
Yeah, you could click on one and see the value of it,

##### **Geohot** [[00:25:12](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1512)]
see how many times it was hit. We'll get there. Yeah, top priority for the rest of the sprint is getting vert training fast. So I think that's the best part. The assembly, yeah. Oh, no.

##### **Qazalin** [[00:25:32](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1532)]
I think the more I think about assemblies, I really want C. But maybe that's just a new problem.

##### **Geohot** [[00:25:42](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1542)]
You really want the what? I really want C syntax. More than what's in the DSL?

##### **Qazalin** [[00:25:55](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1555)]
The DSL doesn't solve like indexing into it. I think the way I think about C is like indexing to this stuff. And it does the pointer math for me.

##### **Geohot** [[00:26:07](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1567)]
Yeah, but assembly doesn't do. It's just not how assembly works.

##### **Qazalin** [[00:26:12](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1572)]
Exactly. I have to worry about all this stuff.

##### **Geohot** [[00:26:16](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1576)]
You're struggling with the pointer math. I mean, again, focus on just making existing gems work fast on vert and then translating them to RDSL.

##### **Geohot** [[00:26:30](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1590)]
Book now how to do it. The key is nevertheless, indexing is never going to get easier.

##### **Geohot** [[00:26:33](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1593)]
I mean, that's just not a way. This is not a way to do like the kind of syntax you want. Because the problem, a lot of the problem is like, when do you compute those indexes? If you read the, so I merge the RDNA fast, the RDNA3 FP32 MAML. And if you look at how much effort is put into indexing, and how many like. indexes are pre-computed and when you plus equals those indexes that stuff matters tons for performance

##### **Geohot** [[00:27:16](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1636)]
i have one question next for llama flash attention

##### **Wozeparrot** [[00:27:25](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1645)]
i saw your multi-device fix i have a test for it just haven't pushed it yet

##### **Chenyu** [[00:27:34](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1654)]
so uh i i try that i trend something uh they trend but even with jit equal to zero in nand at i think seven step

##### **Geohot** [[00:27:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1667)]
oh well i assume that's progress i don't know

##### **Wozeparrot** [[00:27:53](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1673)]
because with j equals zero i've had it train past 50 steps and it's been fine

##### **Chenyu** [[00:27:59](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1679)]
oh then maybe are you training which llama

##### **Chenyu** [[00:28:06](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1686)]
8b oh okay i guess maybe bird is too small i was testing water just because i know the bird output is guaranteed to be correct i see

##### **Wozeparrot** [[00:28:17](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1697)]
but at least with llama 8b i've had it stable without jit

##### **Chenyu** [[00:28:21](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1701)]
can you clean that thing up i think it's a lot of it looks correct but i just don't know too much about the initial design yeah okay yeah i'll clean it up and merge it along the test so the way i did is basically just supervised cloud code and running now equals to one on my computer until it compiles

##### **Geohot** [[00:28:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1727)]
yeah it's probably fine

##### **Chenyu** [[00:28:50](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1730)]
it should run on device as well yeah i mean i tested on the device after i think it looks good and it also compiles so that's why that's after that i send it to you but that's basically how i get that okay okay so let's get this uh fix yeah did you make any progress on jit i did not make

##### **Wozeparrot** [[00:29:16](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1756)]
any progress on jit oh i did track down it's very weird it seems to be just i split qkb backwards into three kernels now one for q one for k and one for v only the v kernel

##### **Geohot** [[00:29:31](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1771)]
outputs incorrect stuff during jit

##### **Wozeparrot** [[00:29:38](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1778)]
even though v and k have essentially the same computation it's very strange i need to look into it more okay

##### **Chenyu** [[00:29:49](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1789)]
I think Cloud would be also pretty useful to debug things like that.

##### **Geohot** [[00:29:53](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1793)]
So just try that. Yeah, try that too. See what the issue is.

##### **Chenyu** [[00:30:01](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1801)]
I think if this device fix looks good and we can fix it, we can come back to good progress.

##### **Chrism** [[00:30:09](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1809)]
Yeah. Okay.

##### **Geohot** [[00:30:15](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1815)]
Sounds good.

##### **Chenyu** [[00:30:19](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1819)]
Next is my stuff.

##### **Chenyu** [[00:30:21](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1821)]
Oh, so I look into Jit. There was this test Jit for gums. I think I made a lot of easy case, lots of easy case no assert and I also include some of the new cases that I found while reading the code. There was a new case, McDonald's English, I mean, desperate code where withs the animation, a bad use case. If you passed a const tensor as an input, because you can never realize a const tensor into a contiguous tensor, that would just fail, because JIT doesn't capture that. Now, JIT also supports things in list and tuple as input. But we don't have a really clear spec on this. For example, should it work if it's a tuple inside a tuple, or list inside a list? How about custom objects and things like that? I initially tried to get parameters, but it got pretty complicated, because of the model way to also get capture. You probably don't want the initial init of those parameters. So currently, I have a test case for that in testJIT, but it only works if it's a list or tuple, not even for set.

##### **Geohot** [[00:31:54](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1914)]
We should probably use nnstate getParameters, and that should just be the shared way to do it.

##### **Chenyu** [[00:32:01](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1921)]
Yeah, but there are things in the getParameters that you don't want to capture in JIT.

##### **Geohot** [[00:32:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1928)]
Why? Because if you do get parameters on args and kw-args, there's things you don't want to capture? Yes. Like what? Wait a second. I think it's one of the . I think it's one of the . I think it's one of the . First, we're not looking to objects,

##### **Chenyu** [[00:32:46](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1966)]
and that's causing a few with how we used to use models. I can give you an example later.

##### **Geohot** [[00:32:54](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1974)]
Jack says these things called pie trees. Yes. And yeah, I mean, it's pretty good. I don't know. Like if you pass the whole model into the JIT, I think it should just capture all those things.

##### **Geohot** [[00:33:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=1988)]
I don't know. Because it also has a lot of parameters. It also looks into like as dict, underscore dict, some weird stuff. Yeah.

##### **Chenyu** [[00:33:20](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2000)]
Yeah, I initially started with getParameters, because that seems to be the unified way to do it. Then there are edge cases that I'm not too sure about. Yeah. So for now, we can always expand this. Because there are also weird cases like I think NandTOPO

##### **Chenyu** [[00:33:45](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2025)]
is derived from one of it, but not the other one.

##### **Chenyu** [[00:33:52](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2032)]
Anyway, it's easier to add supports later. Sounds good. Then there are the rest of the JIT. There are a few things I try. And I don't. I don't really like. There's this like methods, class method. It's reused. I know you suggested check the first if it's self and warm. I don't really know what warm means. We just assert. What do you mean check the first if it's self? So now if it's a class method, let JIT share across the class.

##### **Geohot** [[00:34:32](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2072)]
Oh, yeah. That's something like kind of use it that way. It's weird.

##### **Chenyu** [[00:34:43](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2083)]
Yeah. That's more of a corner case. Then there's this case that should JIT in JIT be fail in the first call or the second call. I try to move everything checked to the first call. Then it end up being weird. Because there you really want to set J equals to 1 to be a different path and not doing this check. Things like that.

##### **Geohot** [[00:35:10](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2110)]
I had two ideas for JIT improvements.

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2117)]
So one is if you pass in things that are different sizes to insert, you could create another JIT context for it. And this would kind of help with that class issue. Because it's fine if the JIT object is shared. It just creates multiple JIT objects depending on the sizes that you pass in of stuff.

##### **Chenyu** [[00:35:46](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2146)]
Do we have a legit use case for that?

##### **Geohot** [[00:35:49](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2149)]
Yeah. So if you use, like in Lama, if you pass in different batch sizes or anything of your batch, pass in different batch sizes.

##### **Geohot** [[00:36:03](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2163)]
OK.

##### **Geohot** [[00:36:05](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2165)]
However. That's only going to work if the JIT actually frees the intermediate memory. If it captures all the intermediate memory, you can't create 10 JITs. So that's the second idea. Like I wonder if we could free and reallocate the intermediate memory quickly enough to still make the JIT performant. Intermediate memory should become one big slab of memory. That's all just indexed into. And then if we deallocate it and reallocate it on every JIT call, 98% of the time, you're going to hit the LRU. So just or right now, like we have a call for this, free intermediates. I wonder if we could get it fast enough so we could always free intermediates.

##### **Chenyu** [[00:36:57](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2217)]
But you can imagine, say, when you are training, you know you are not never going to change your size. So even if it's fast enough, you might as well not do that.

##### **Geohot** [[00:37:09](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2229)]
But if it's free, though, I mean, imagine like,

##### **Geohot** [[00:37:12](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2232)]
forget the size thing. I mean, the size thing is just like the, that becomes easy once you're automatically freeing intermediates. But yeah, automatically freeing intermediates.

##### **Geohot** [[00:37:23](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2243)]
How cheap could that be?

##### **Chrism** [[00:37:34](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2254)]
OK.

##### **Geohot** [[00:37:35](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2255)]
I don't know. I can look into this. Yeah, no, just an idea. If it's not useful, just start working on it.

##### **Chrism** [[00:37:46](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2266)]
OK.

##### **Chenyu** [[00:37:53](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2273)]
I don't think any of those leads to the actual LRMJIT issue. But since seems to have a good lead on that, we'll see what we get later. Another thing. I tried with Cloud is to use it to solve some. The exact case I was testing was make disk assign, I guess, disk slice assign lazy. I think that's a good exercise for it to trace along all the copy, different paths for copy. We have tons of different special case for copy. And so, yeah. I think it's a good idea to use it. Let's see how we use it in terms of scheduling change or range by change. All I can say is it weighs tons of kernels. It seems to understand issue, but it's too hard for it to do anything useful. I think facing schedule issue, I guess we discussed this last week. But the best tools it has is this equals to minus 1, then try to parse the pickle.

##### **Geohot** [[00:39:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2348)]
So that was not very useful. Yeah, Klaus, any progress on that, giving Cloud more context?

##### **Chenyu** [[00:39:19](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2359)]
At least I can work more. I don't have a concrete feedback now for what I want. But I think one thing we can think more as people adopt Cloud coding more is, if you're not using, for example, the same code as the same code, are we wasting too many tokens in our output debug messages? Or the way we represent data, is it optimal? We used to design debug levels and things kind of randomly or semi-randomly. And some of these can probably be improved.

##### **Geohot** [[00:39:58](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2398)]
So Harold's take on this that I really agree with is that you should never design for the AI. You should only design for humans. Because what's good for humans is good for the AI.

##### **Chenyu** [[00:40:09](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2409)]
Yeah, but the old debug level, other than the debug institute 2 and debug institute 4, the source code is not really human readable.

##### **Geohot** [[00:40:19](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2419)]
Yeah, I mean, and that's a problem, right? But we should fix it for humans.

##### **Geohot** [[00:40:22](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2422)]
We shouldn't fix it for AIs. Like, yeah, anything we can do to...

##### **Geohot** [[00:40:29](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2429)]
I mean, yeah, debug equals 3. Like, what really is debug equals 3? Debug equals 3. Debug equals 1 means something. 3 is just the only one that's kind of...

##### **Chenyu** [[00:40:37](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2437)]
There's also the issue that Viz is designed for humans, right? But Viz is not really helpful for AI coding.

##### **Geohot** [[00:40:44](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2444)]
Well, the Viz front end is not.

##### **Geohot** [[00:40:47](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2447)]
But all of, like, Viz is mostly the capturing stuff. Anyway, I think that's...

##### **Chenyu** [[00:41:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2462)]
Something we can work more, or if people have ideas, when you, like, spend or waste all sorts of tokens and interact with it. See if we can make the debug information more useful. I think this might also be similar to, like, designing the UI, UX for assembly. Like, people struggle with assemblies. Like, it's very hard to read and structure with. Maybe, like, similar principles. How do we capture the things that is useful to make progress?

##### **Geohot** [[00:41:37](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2497)]
Yeah, I mean, I think... It's actually... It's shocking how bad Claude is at writing any assembly. And it's bad at writing assembly for the same reasons humans are bad at writing assembly. Like, it just, like, you know, gets confused and copy and pastes instructions in places. And then things don't work. And it didn't carefully think everything through. And then it just, like... So, yeah, I think there... Whatever makes it easier for humans will also make it easier for models. Starting with just, like, type checking. Right? Like, now, like, my assembly DSL, when you run it, if you put an S where you were supposed to put a V, it throws an error. Yeah.

##### **Chenyu** [[00:42:20](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2540)]
There was... Someone said Rust would be the good language for agent coding because if it compiles, it's just for it to work. It's just higher.

##### **Geohot** [[00:42:29](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2549)]
Yeah. I don't know. I have the same... My thoughts always on that kind of stuff are, like, there's a reason humans code in Python.

##### **Chrism** [[00:42:40](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2560)]
Yes.

##### **Geohot** [[00:42:43](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2563)]
I could imagine the agent spending... Wasting tons and tons of time trying to figure out how to get the borrow checker to be happy when in Python it just could have written something, written tests for it.

##### **Chenyu** [[00:42:57](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2577)]
Yeah.

##### **Geohot** [[00:42:57](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2577)]
Yeah.

##### **Chenyu** [[00:42:59](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2579)]
But I know what Cloud is good. Oh, so my... Another side project is go through all the to-dos in TinyGrad and try to do Lowe's. Cloud is really good at updating tests for, like, a simple concept. Just imagine the old linearizer failure test that's very hard to update. It's very easy for Cloud to do. Oh, yeah.

##### **Geohot** [[00:43:22](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2602)]
Yeah.

##### **Chenyu** [[00:43:23](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2603)]
So updating Lowe's. And it's also pretty good writing Annex Ops because it will pull the Ops bags and read the test case and, like, write the thing for it. You just need to supervise it and tell it to write it better or the way you want. But let's look at the issue as no matter how many times I tell Cloud to read the div and make it minimal, it will fail at some point. Then I point out, okay, how about consider writing it that way? Then they can write a good code.

##### **Geohot** [[00:43:56](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2636)]
Yeah. There's a few times where I just, like, I'll yell at it repeatedly about the same five lines. It'd be like, no, you can write that in three. Like, it's obvious what it is and it just doesn't see it. Yeah. Yeah.

##### **Chenyu** [[00:44:07](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2647)]
But I think it's a good exercise anyway to go through. I think we have a lot of some of the old to-do code or the skip test just because we were, like, not having enough time to update Lowe's properly. I think it's a good time to have help with agents. I mean, I pay for the max plan anyway, so I might as well use those tokens on the side.

##### **Geohot** [[00:44:33](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2673)]
Yeah. No, it's the limit is not the AI tokens. The limit is how carefully you want to review its work. Yeah. And I mean, that's the problem.

##### **Chenyu** [[00:44:44](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2684)]
I think we are getting better. And I mean, this run, it really fixed a lot of really old test cases. Some of it was even, like, not even correct. It's just it's always there and no one bothered to read it. So I think it's a good exercise.

##### **Geohot** [[00:45:01](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2701)]
Oh, yeah. I mean, the test, the general quality of the test code in TinyGrad is not that high.

##### **Chrism** [[00:45:06](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2706)]
Yeah.

##### **Geohot** [[00:45:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2708)]
Okay. I've been trying the thing. I have all these tests now for, like, the cycle accurate emulator. And I try to get Claude to write a hardware model that matches these tests. And I've burned hours on it. Can't do it. Not smart enough.

##### **Chenyu** [[00:45:25](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2725)]
Okay.

##### **Chenyu** [[00:45:28](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2728)]
Let's move on to your assembly stuff.

##### **Geohot** [[00:45:32](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2732)]
Yes, I did. I've been going through the files one at a time. And I shoved the AI crap out. So now, like, PDF is very high quality. And today I worked on Inst. I worked on DSL. DSL is very high quality. And PDF and DSL are everything you need for PDF is like the auto generator. And then DSL is the, like, the Python syntax for writing assembly languages. Yeah, PDF and DSL hopefully by the end of this week can move into real TinyGrad. And then we can start using them. And we already use them. But we can use them, like, everywhere. I think that it's just kind of nicer than LLVM syntax. The SQTT one is also really small. I wrote some tests this weekend that do that compare. Our SQTT to Rock, Prof, TraceDecoder. And it matches perfectly. So, yeah, those three are pretty small. And then I have two files, Asm and Disasm, which are an LLVM style assembler and disassembler. And they're just trash heaps. So I don't know about those ones. I don't even know if that's functionality we really want. Or rather just improve the DSL pretty printer to the point. We just use that. And those are nice because they can actually execute in Python. But, yeah, it's a complete integrated runtime environment for AMD assembly. I think it'll be in core TinyGrad by the end of the month. And then start working on an actual assembly backend or whatever that means. Maybe it's just taking the two-step process. TinyKit and stuff and starting to in the registers. Yeah, you know, you need a register allocator. So if we could, if we just like, if we have the registers and we have the instruction ordering, it should be really easy to just directly turn that into assembly. And I bet it'll be faster a lot of times than what LLVM generates. Because the LLVM is not designed. There's nothing in LLVM that's capable of reasoning about like warps. It's just designed to do that. It's not designed for like interleaving. Which like, kinda uses the resources, but not really. I also from the SQTT stuff finally really understand what warps are. So like, the whole GPU has one ALU pipe that all of the warps share. And the warps all submit stuff to that single ALU pipe. And the idea is to keep that pipe full all the time. Like, I guess I knew this. It's so nice when you can actually see it from the SQTT trace and see stuff going in. End of the month, be a complete environment. And then write it back and then I'll put the assembly.

##### **Geohot** [[00:48:35](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2915)]
And then we have real zero dependency AMD. Will it be fast? Uh, it should.

##### **Geohot** [[00:48:52](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2932)]
Yeah. I mean, check out... So AMD as a matmall is a copy from the Seb blog post stuff. But yeah, it's very fast. Actually, by just cleaning up his stuff, I've managed to get another 10% of speed on top of his stuff. So I'm getting like... I didn't get his 50 teraflops. I got like 45, but then I managed to get it up to like 50. So it should. Yeah. I mean, it should. It should. If it's not fast, we'll finally have a way to understand why it's not fast. Like, if you write something in C and it's not fast, like, okay, why is it not fast? Good luck. The GPU execution model is so complex.

##### **Chrism** [[00:49:44](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2984)]
It's not fast. It's not fast.

##### **Geohot** [[00:49:51](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2991)]
Sounds good.

##### **Chenyu** [[00:49:56](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2996)]
Anything else for you?

##### **Geohot** [[00:49:59](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=2999)]
Well, then, like, looking forward to kind of the end of the year, I think this is going to be the year of LLVM removal. By the end of this year, I want to be able to output Nvidia stuff, too. I want to be able to output SAS. That has to be reverse engineered. And hopefully the DSP stuff, too. And then if you can do all of those, then... In 2027, we're finally ready to write on to do our hardware. We have to get real performance on these kernels. I don't know. Maybe AMD will be excited about these things. Posting, like... We should be able to get the highest performing map on CDNA.

##### **Geohot** [[00:50:42](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3042)]
There's a ton of stuff that these things all leave on the table because they're all LLVM based.

##### **Chrism** [[00:50:46](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3046)]
Mm-hmm.

##### **Geohot** [[00:50:48](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3048)]
There's no environment for AMD that's not LLVM based. There's some that use inline assembly. But I haven't seen any that just completely do all this stuff in assembly.

##### **Geohot** [[00:51:07](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3067)]
So, yeah, we can get the fastest... The fastest gem on CDNA 4. Sounds good. Now, what do we have for bounties?

##### **Chenyu** [[00:51:27](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3087)]
Oh, I merged the FP8.

##### **Chenyu** [[00:51:31](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3091)]
I mean, I run the script. It seems to be using FP8 for the linears. So, I think it's fast. It's fast? Yeah. It's a bit faster. But now, training birds really is all bottleneck flash attention. So, yes, the gem is faster, but it's the flash attention still. Or maybe not all flash attention, but it's more difficult to assess because bird is so small.

##### **Geohot** [[00:52:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3122)]
Yeah. I mean, I don't buy this theory that bird is so small. That's why the flash attention is so small. I mean, I don't think the flash attention is unstable.

##### **Geohot** [[00:52:11](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3131)]
It doesn't make sense to me. I think the problem...

##### **Geohot** [[00:52:17](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3137)]
The flash attention being unstable because bird is small, that doesn't make sense to me. I bet there's some instability with, like, how the max thing is being done. I bet the max thing is being done wrong. Oh, maybe. Like, there's a lot of ways to subtly do flash attention wrong that's going to get you to the max. But it's not going to get you these kind of nans that doesn't have anything to do with the JIT or doesn't have anything to do with...

##### **Geohot** [[00:52:46](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3166)]
No, like, what do you mean it's too small? I just don't buy that. Oh, you are talking about the nan issue earlier? Yeah.

##### **Chrism** [[00:53:07](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3187)]
Yeah.

##### **Geohot** [[00:53:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3188)]
Yeah.

##### **Geohot** [[00:53:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3188)]
Yeah. I don't know.

##### **Chenyu** [[00:53:10](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3190)]
Maybe flash attention has a bug or something.

##### **Geohot** [[00:53:13](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3193)]
Probably does. Yeah. Probably flash attention backward has a bug. Flash attention forward is easier to write. Flash attention backwards...

##### **Geohot** [[00:53:25](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3205)]
Yeah. We'll see. Hopefully we get that.

##### **Geohot** [[00:53:34](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3214)]
But yeah, I just don't buy this whole thing that bird is so small. It's a bug. Yeah.

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3222)]
Yeah. Yeah. I agree. How about you, B1T? Do you have anything to add for float eight? Hello.

##### **Chenyu** [[00:54:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3240)]
Hi.

##### **B1tg** [[00:54:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3242)]
Hi, B1T. I added seed to the BERT data server. So we can compare it with half rounds.

##### **Chenyu** [[00:54:20](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3260)]
Have you confirmed that with the same seed you will get exactly the same loss?

##### **B1tg** [[00:54:28](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3268)]
Yes, with the same seed the loss and the LRM accuracy stay the same. I posted a picture. There are few rounds with different seed.

##### **Chenyu** [[00:54:48](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3288)]
Yeah, so the flop is higher.

##### **Geohot** [[00:55:05](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3305)]
I'm aware of this.

##### **Chenyu** [[00:55:06](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3306)]
Then I also trend that branch on myself. So that I merge this. I also know that you didn't split the setup. So there's no cache. And if I round it twice with the cache, it will be faster. What really matters is the step time. That's fine.

##### **B1tg** [[00:55:30](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3330)]
Yes. And the clamp, since the clamp you changed a few weeks ago, make the kernel slower. If I change the clamp to minimal and max, it will be faster.

##### **Geohot** [[00:55:56](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3356)]
Oh, I don't remember anything.

##### **Chenyu** [[00:56:00](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3360)]
Maybe I did.

##### **B1tg** [[00:56:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3362)]
A few weeks ago, I asked that we should match the clamp API backwards behavior with touch.

##### **Chenyu** [[00:56:16](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3376)]
Oh, yeah. Are we matching torch now or no?

##### **B1tg** [[00:56:22](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3382)]
We match touch now.

##### **Chenyu** [[00:56:24](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3384)]
But it's slower.

##### **B1tg** [[00:56:26](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3386)]
But it's slower, yes.

##### **Chenyu** [[00:56:31](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3391)]
Well, I don't know. If you can make it faster, then that's great. Otherwise, I think matching torch behavior on these numericals is preferred even though it's slower for now. It's just one ALU.

##### **B1tg** [[00:56:46](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3406)]
So generally, FP8 is more fun. It's faster than FP16.

##### **Chrism** [[00:56:58](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3418)]
Cool.

##### **Geohot** [[00:57:02](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3422)]
Sounds good. Are the bounties doing that? Do people still do bounties? Not really. Yeah, I think it's kind of a shock at the moment. It's hard with all the AI stuff. Like, the problem is we just get so many submissions now.

##### **Geohot** [[00:57:37](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3457)]
We had to delete that other bounty because we get so many submissions from people who just like casually threw clot at it and then just was like, oh, OK, I don't know. Submit it when all the value is actually in the validation on the work.

##### **Geohot** [[00:57:49](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3469)]
Now.

##### **Chenyu** [[00:58:08](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3488)]
I will review the whisper one. That seems to be fine. I just comment on it. I think some of the cleanup can be separate into smaller PRs. That also helps TinyGraph proper. I think this is still true for anyone who wants to contribute. If you can split your PR into individually useful pieces, just do that. Because you know that the bottleneck is the maintainers and reviewers reading the code. If you make it simpler, smaller, easier to understand, the chances for it to be picked up by someone is higher. If you just open a PR that has like 500 lines and has questionable benefits, no one... It's not even like people won't close it.

##### **Geohot** [[00:58:56](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3536)]
People will just skip it. So don't do that. I think that's it for this meeting.

##### **Chenyu** [[00:59:13](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3553)]
We will discuss about the meeting time next week. I think we're realistic. It's either the same time or maybe one hour earlier. We will discuss it later.

##### **Geohot** [[00:59:26](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3566)]
Sounds good. Yeah, I'm so tired.

##### **Chenyu** [[00:59:30](https://www.youtube.com/watch?v=MLaBoY1Hb9U&t=3570)]
OK. That's it for this one. Thank you, everyone. See you next week. Bye bye.
