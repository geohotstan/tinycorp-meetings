# 2026-01-26 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- llama training
- assembly
- drivers
- viz / fast gemm
- jit asserts, assign, mypy
- image dtype
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=IAbOilYNLdc)

### Highlights

- **[Company focus + January sales](#geohot-000008)**: Posted cloud analysis; big priority is proving high-MFU LLM training on 64+ GPUs (not just 405B), and January sales are reported at **$430,000**.
- **[“Seven black whale bucks”](#geohot-000152)**: Frames January sales as “seven black whale bucks.”
- **[Pricing + product mix](#geohot-000157)**: Mentions honoring earlier Blackwell pricing, charging more for other units, selling “reds” and “pros,” and suggests momentum could **double revenue** this year.

- **[LLaMA training status: slow step time](#wozeparrot-000313)**: K192 training is around a **10-second step**, needs investigation (attention vs other components).
- **[Embedding + GEMM are bottlenecks](#wozeparrot-000337)**: GEMMs look slow and embedding is taking a long time.
- **[Possible embedding fix flag](#chenyu-000402)**: Suggests trying the `split_reduce_up_eq_0` flag to address slow embedding.
- **[Training runtime math + gradient accumulation](#geohot-000518)**: With ~12k steps, 10s/step is ~33 hours, but batch-size constraints imply gradient accumulation work is needed.
- **[Driver stability difference](#wozeparrot-000636)**: Training with “AM” is stable; stock AMD driver was crashing.

- **[8K context window OOM on MI300](#geohot-000922)**: 8K context is too slow and also hits OOM on MI300; discussion centers on MI300 having less memory than MI350.
- **[MI300 crashes may be hardware/ECC](#nimlgen-001131)**: Reports data fabric + ECC errors, implying machine/hardware issues rather than software.
- **[Stability plan for the crashing machine](#geohot-001223)**: Asks for repeated runs and experiments like lowering max clock/temperature/power to isolate the cause.

- **[Assembly: emulator is working + default remu](#geohot-001326)**: Emulator now works broadly; PR to set Python `remu=1` by default; emulator helps find many bugs and is progressing on RDNA4 support.
- **[Scratch explained as a “never fast” red flag](#geohot-001656)**: Finds Winograd crashes because LLVM output uses Scratch; calls Scratch usage a mistake and motivates an assembly-output backend.
- **[DType changes + const-float for ±0](#geohot-001826)**: Changes int64 promotion behavior (int64 → uint64) and adds a `const float` class to distinguish `0` vs `-0` in Python caches/hashing.
- **[Decomp correctness + LLVM fast-math edge bugs](#geohot-002037)**: Mentions `emu2` flag to use LLVM backend in the emulator and notes subtle fast-math-related correctness issues to test.
- **[Negative-zero sqrt issue](#geohot-002134)**: Notes current sqrt decomposition via `pow(x, 0.5)` doesn’t preserve the sign for `-0`, suggesting adding tests.

- **[Drivers: SQTT-style tracing + decoder work](#nimlgen-002240)**: Merged SQTT-related infrastructure/tests; decoder work is ongoing and not fully passing yet.
- **[Raw bytes + mapping to PC is the hard part](#nimlgen-002503)**: Pulling raw bytes from the GPU; main challenge is matching samples to the correct PC address.
- **[Kernels should be interruptible + not kill the GPU](#geohot-002717)**: Wants a way to halt kernels and ensure bad kernels don’t bring down the whole GPU or hang for ~30 seconds.
- **[Action items: decomp tests + GPU-crash tests](#geohot-003125)**: Writes down tasks: decomp tests, tests for GPU crashes (no full GPU reset/hang), and embedding work on MI350X.
- **[Single-step / breakpoints via SQ commands](#geohot-003314)**: Discusses using SQ commands to set breakpoints and potentially single-step kernels for debugging.

- **[Apple entitlement format mismatch](#nimlgen-003352)**: Apple approval is blocked by an entitlement formatting issue (integer granted vs mask expected); awaiting clarification.
- **[USB4 reliability issue on boards](#wozeparrot-003604)**: Reports inability to reliably link at USB4 even after suggested mods; plans to escalate to Robo/Adeeb.

- **[Viz: move to RDSL, no LLVM](#qazalin-003728)**: Visualization stack shifted to RDSL with “no LLVM ever,” with upcoming cleanup of SQTT/RDSL tooling.
- **[Viz UX requests: context view + navigation](#geohot-004052)**: Wants showing surrounding instructions (e.g., ~20 before/after) with offsets, plus better linking between VALU events and wave instructions + arrow-key navigation.
- **[Fast GEMM approach: prune Torch kernels via SQTT](#qazalin-004508)**: Torch-generated kernels are ~20k lines; using SQTT to identify needed branches and remove complexity to fix JIT/race issues.
- **[Alternative path: inject compiled blobs (Mojo/Torch)](#geohot-004637)**: Suggests dumping machine-code blobs from Mojo (or elsewhere) and “shoving the blob in” rather than relying on LLM-generated assembly.
- **[MMA peak + ELF: reducing LLVM dependency](#qazalin-004805)**: MMA peak now uses DSL packing bytes directly; ELF PR is mechanical and intended to move closer to a full in-house stack.

- **[JIT footgun guard: forbid `_buffer` access](#chenyu-005037)**: JIT now asserts if code accesses underlying `_buffer` (e.g., `.item()`, `.tolist()`), to prevent silent incorrect replay behavior.
- **[Assign + “remove realize from setitem” direction](#chenyu-005325)**: Focus is making assign/setitem fully lazy with correct scope tracking, fixing both kernel-level correctness and scheduler tracking so realizes aren’t needed as hacks.
- **[Long dtype via decomposition: correctness over speed](#chrism-010156)**: Integer ops via decomp mostly work; remaining edge cases (signed long division/casts) are being ironed out.
- **[Why this matters: remove dtype/device special-casing](#geohot-010353)**: Goal is identical API across devices (e.g., WebGPU), avoiding “one stupid long in ONNX” breaking compilation—speed is secondary.
- **[Qualcomm half: handle via decomposition/bitfiddling](#geohot-010656)**: Prefers renderer-side decomposition strategies (no “backpressure” to higher layers) rather than declaring dtypes unsupported upstream.
- **[Testing gap: dtype coverage needs expansion](#chrism-010925)**: Notes dtype tests missed ops like negation (WebGPU lacked negation), and calls for broader ALU coverage tests.

- **[Anthropic VLIW challenge takeaway](#geohot-011023)**: Enjoyed the challenge; highlights that TinyGrad can produce state-of-the-art solutions and an external PR even beat his solution.
- **[Hardware optimism](#geohot-011115)**: Says their own hardware “looks closer than ever,” though there’s still a lot to do.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=IAbOilYNLdc&t=0)]
Welcome everyone. Star Wars company update.

##### **Geohot** [[00:00:08](https://www.youtube.com/watch?v=IAbOilYNLdc&t=8)]
Yes, I posted the cloud analysis. I put the meetings repo into cloud. Yeah, I mean, I think we can do it, but I think this is super important that we get this done. And then pretty much I think for the rest of the year, we're just going to be cleaning this up. You know, because it's not just about training 405B LLMA. What does everybody want to do? They want to train LLMs on large quantities of GPUs. So that's kind of what we should be, what we should be targeting. And if we can't do that, you know, so, so, Eporat came in and asked, like a fully fledged training example of training LLMs with high MFU for 64 plus GPUs. So, you know, that's kind of our, kind of our target. We've sold a whole bunch of tiny boxes. They're selling pretty well. Yeah, we're off to a good year revenue wise. We log into the shop here and tell you what our revenue to date is. So, just in January, I'll make sure this is right because this is a big number. Yeah, just in January, our sales have been $430,000.

##### **Geohot** [[00:01:52](https://www.youtube.com/watch?v=IAbOilYNLdc&t=112)]
So that's seven black whale bucks, more or less.

##### **Geohot** [[00:01:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=117)]
Let me see, get the breakdown here. So, that's $7,000. I don't know if you guys have seen the review of the Blackwell. There's no one buys red, right?

##### **Chenyu** [[00:02:02](https://www.youtube.com/watch?v=IAbOilYNLdc&t=122)]
And the Blackwell is the only product.

##### **Geohot** [[00:02:05](https://www.youtube.com/watch?v=IAbOilYNLdc&t=125)]
We sold a few pros too. Were they before the price change? No, actually, we, I didn't even sell them to them at 50. The people who bought the Blackwell at the cheaper price, I honored it. But the people who bought the other ones at 50, I was like, no, you got to, you got to pay me more. And they all paid 60. Yeah, we sold a bunch of reds recently too. But yeah, so big month for us. If this sort of stuff keeps up, we could be looking at like doubling our revenue this year.

##### **Geohot** [[00:02:49](https://www.youtube.com/watch?v=IAbOilYNLdc&t=169)]
Great.

##### **Chenyu** [[00:02:58](https://www.youtube.com/watch?v=IAbOilYNLdc&t=178)]
Anything else we're accompanying? I think we already reviewed some of this. Nope. This time it's a random order by ChetGPT, and we'll start with lab mod training.

##### **Wozeparrot** [[00:03:13](https://www.youtube.com/watch?v=IAbOilYNLdc&t=193)]
So we have some models training. K192 still takes still a 10 second step, which is really slow. I need to look back into it to see how much of it is attention. But, did drop 8x.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=IAbOilYNLdc&t=213)]
Yeah, I mean, our gems don't look that fast either.

##### **Wozeparrot** [[00:03:37](https://www.youtube.com/watch?v=IAbOilYNLdc&t=217)]
The gems are pretty slow, and the embedding is still taking a really long time.

##### **Geohot** [[00:03:46](https://www.youtube.com/watch?v=IAbOilYNLdc&t=226)]
How many steps do we have to take? We have to take about 12k steps.

##### **Geohot** [[00:03:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=237)]
12k.

##### **Chenyu** [[00:04:02](https://www.youtube.com/watch?v=IAbOilYNLdc&t=242)]
Do you know why embedding is slow? Do not. Have you tried split reduce up equal to 0?

##### **Wozeparrot** [[00:04:13](https://www.youtube.com/watch?v=IAbOilYNLdc&t=253)]
Is that a flag? I didn't know that was a flag.

##### **Geohot** [[00:04:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=257)]
It's a flag.

##### **Geohot** [[00:04:18](https://www.youtube.com/watch?v=IAbOilYNLdc&t=258)]
It is a flag. Also, so.

##### **Chenyu** [[00:04:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=261)]
It's very possible that because embedding needs a range to stay equal. One a range to be kind of surprising. I would suspect that's the thing first, because this has a very big vocab size, if I remember correctly.

##### **Geohot** [[00:04:39](https://www.youtube.com/watch?v=IAbOilYNLdc&t=279)]
Yes.

##### **Geohot** [[00:04:41](https://www.youtube.com/watch?v=IAbOilYNLdc&t=281)]
Is it padded to something stupid? Is the vocab size like some weird number?

##### **Wozeparrot** [[00:04:46](https://www.youtube.com/watch?v=IAbOilYNLdc&t=286)]
It could be that too.

##### **Chenyu** [[00:04:47](https://www.youtube.com/watch?v=IAbOilYNLdc&t=287)]
It is a more annoying vocab size. So I think it's reasonable to just, I think a better strategy for this is. The jam is slow, attention is slow, embedding is slow. Then find an easy way to just test that. Verify it's the same slowness. We can see what's the stupid part and make it slow. I bet a lot of it is random scheduler thing.

##### **Wozeparrot** [[00:05:15](https://www.youtube.com/watch?v=IAbOilYNLdc&t=315)]
Yeah. Vocab is 128, 256.

##### **Geohot** [[00:05:18](https://www.youtube.com/watch?v=IAbOilYNLdc&t=318)]
Yeah, the size is pretty normal. Divides by 256. So even at 10 seconds, if it's 12,000 steps, it's not bad. That should only take 33 hours to train.

##### **Geohot** [[00:05:35](https://www.youtube.com/watch?v=IAbOilYNLdc&t=335)]
Would we double that? Because we can't fit bs16 without gradient accumulation.

##### **Geohot** [[00:05:45](https://www.youtube.com/watch?v=IAbOilYNLdc&t=345)]
Oh, OK. So that's 12k bs16 steps. Yes. OK. Yeah, OK. And I think working on gradient accumulation makes sense.

##### **Wozeparrot** [[00:05:55](https://www.youtube.com/watch?v=IAbOilYNLdc&t=355)]
Yeah, that's all right. I was doing that. Because I wanted to match the NVIDIA reference as much as possible.

##### **Geohot** [[00:06:00](https://www.youtube.com/watch?v=IAbOilYNLdc&t=360)]
Right. But yeah, OK. So it looks like we're still on track. So it looks like we're on track to have a LLAMA 8B train this sprint. Do we have 1024s converging?

##### **Wozeparrot** [[00:06:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=371)]
Yeah, I've been trying some stuff. But I think it just takes really long, because you need to hit the same amount of tokens seen as with 8192. And you're just hitting 8x less tokens with 1024.

##### **Geohot** [[00:06:23](https://www.youtube.com/watch?v=IAbOilYNLdc&t=383)]
Is this with the AM driver or with AMD?

##### **Wozeparrot** [[00:06:27](https://www.youtube.com/watch?v=IAbOilYNLdc&t=387)]
I'm training with AM. I've had crashes with AMD.

##### **Geohot** [[00:06:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=391)]
I see. I have crashes with AM as well. But this might be an MI300 versus MI350.

##### **Wozeparrot** [[00:06:36](https://www.youtube.com/watch?v=IAbOilYNLdc&t=396)]
Yeah, AM has been really stable for me. Using the stock AMD driver has been crashing. Great.

##### **Geohot** [[00:06:45](https://www.youtube.com/watch?v=IAbOilYNLdc&t=405)]
Cool. Yeah, glad to hear that. Yeah, then I think we're on track to have this. I can look at embedding. Yeah, if you work on attention, Quaslan, if you work on this, I'll work on gem. I'll work on embedding. Yeah, and embedding is just like, yeah, I can do that.

##### **Chrism** [[00:07:08](https://www.youtube.com/watch?v=IAbOilYNLdc&t=428)]
Great.

##### **Geohot** [[00:07:12](https://www.youtube.com/watch?v=IAbOilYNLdc&t=432)]
Yeah, so if we can get this down to something like 10 seconds for the gradient accumulation step, then we totally should be able to have this trained by the end of the sprint.

##### **Chenyu** [[00:07:28](https://www.youtube.com/watch?v=IAbOilYNLdc&t=448)]
Yeah. Oh, when you say three seconds for embedding, is it forward or forward plus backward? Forward plus backward.

##### **Geohot** [[00:07:36](https://www.youtube.com/watch?v=IAbOilYNLdc&t=456)]
I think our embedding backward is just not good. I think that's very possible. Yeah, I can work on that. I can work on that on MI300. I can work on that by setting Lama layers to something small. So.

##### **Chrism** [[00:07:56](https://www.youtube.com/watch?v=IAbOilYNLdc&t=476)]
OK. OK.

##### **Geohot** [[00:08:05](https://www.youtube.com/watch?v=IAbOilYNLdc&t=485)]
Reading through your comments, do we

##### **Chenyu** [[00:08:08](https://www.youtube.com/watch?v=IAbOilYNLdc&t=488)]
have any other thing we need to fix? So now QKB is in one kernel, right? I saw a change. Is that the latest?

##### **Wozeparrot** [[00:08:20](https://www.youtube.com/watch?v=IAbOilYNLdc&t=500)]
That was not actually faster. That was quite a bit slower. I'm going to figure out why. But split QKB doesn't really seem to affect anything. They use the same amount of memory too.

##### **Geohot** [[00:08:42](https://www.youtube.com/watch?v=IAbOilYNLdc&t=522)]
I mean, you're re-computing one of the gems or not. Yes.

##### **Wozeparrot** [[00:08:48](https://www.youtube.com/watch?v=IAbOilYNLdc&t=528)]
But the problem with merge, I don't know how much of the slowdown is because Q is now atomically stored.

##### **Geohot** [[00:08:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=537)]
So I'm not sure if that's going to be a problem. Not even quite sure what that means.

##### **Geohot** [[00:09:00](https://www.youtube.com/watch?v=IAbOilYNLdc&t=540)]
But yeah, no, I don't think that this is that important.

##### **Chenyu** [[00:09:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=557)]
And 8K context window fits is just too slow?

##### **Geohot** [[00:09:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=562)]
Yes. Do we know why it doesn't fit on MI300?

##### **Chenyu** [[00:09:32](https://www.youtube.com/watch?v=IAbOilYNLdc&t=572)]
Is it just off by a little bit? Is it almost the limit?

##### **Geohot** [[00:09:41](https://www.youtube.com/watch?v=IAbOilYNLdc&t=581)]
I mean, I don't know. It just gives an out of memory error. That's hard to debug. MI300 has a lot less memory? I think it's 192 versus 288. Yeah.

##### **Wozeparrot** [[00:09:59](https://www.youtube.com/watch?v=IAbOilYNLdc&t=599)]
Yeah, MI300 doesn't have enough memory. We're at 1.9 terabytes.

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=IAbOilYNLdc&t=607)]
1.9 terabytes. Let's see. Yeah, OK, so that's 1.5 terabytes. Do we know if we're using memory efficiently or we're?

##### **Wozeparrot** [[00:10:18](https://www.youtube.com/watch?v=IAbOilYNLdc&t=618)]
Not sure about that either. It's possible that we're storing more for back end. Backward than needed. Yeah, I think we're storing more if our goal is.

##### **Chenyu** [[00:10:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=631)]
That's still too much.

##### **Geohot** [[00:10:34](https://www.youtube.com/watch?v=IAbOilYNLdc&t=634)]
Just not clear where. Yeah. And this is Bflow 16, right? So model is just like 16. Yeah, Bflow 16. Oh, no.

##### **Chrism** [[00:10:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=657)]
Yeah.

##### **Geohot** [[00:11:02](https://www.youtube.com/watch?v=IAbOilYNLdc&t=662)]
Yeah, I don't know if we'll wait to drivers to get to this, but I'm seeing tons of crashes on my 300. I mean, if it's quite stable, maybe Nemojin

##### **Chenyu** [[00:11:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=681)]
can take a look.

##### **Geohot** [[00:11:24](https://www.youtube.com/watch?v=IAbOilYNLdc&t=684)]
Yeah. Yeah, Nemojin, do you have any ideas? I can pretty repeatedly run it and it'll crash on my 300.

##### **Nimlgen** [[00:11:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=691)]
Actually, I've had it some hardware events and actually merged this. So yeah, actually, the problem looks like the same as AMD GPU driver. So we actually have the data fabric reports and ECC error. Yeah, and that's it.

##### **Geohot** [[00:11:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=713)]
Interesting.

##### **Geohot** [[00:11:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=713)]
So OK, it's actually a real, it's just that machine that's broken then.

##### **Nimlgen** [[00:11:59](https://www.youtube.com/watch?v=IAbOilYNLdc&t=719)]
Yeah, but actually, I think that, I don't know, I haven't run the second run with AM yet, but like AMD GPU reported the different GPU. So maybe because of temperatures or something.

##### **Geohot** [[00:12:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=734)]
Yeah, I'll leave the machine to you if you could try a bunch of runs and see if you can figure out what this is.

##### **Chrism** [[00:12:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=741)]
OK.

##### **Geohot** [[00:12:23](https://www.youtube.com/watch?v=IAbOilYNLdc&t=743)]
If you want to lower the max clock or the temp, lower the power or something.

##### **Geohot** [[00:12:32](https://www.youtube.com/watch?v=IAbOilYNLdc&t=752)]
Yeah, I'll try that. Well, yeah, no, it would be great to get a stable run

##### **Geohot** [[00:12:37](https://www.youtube.com/watch?v=IAbOilYNLdc&t=757)]
because you should not have these runs crashing. Sorry. Just use that same command.

##### **Geohot** [[00:12:45](https://www.youtube.com/watch?v=IAbOilYNLdc&t=765)]
It doesn't seem to be a software issue. Maybe some race condition or some hardware. It doesn't seem to be an issue with the long between you. Yeah. I thought it might have been eval stuff or something, but it doesn't look like it. OK, so I'll leave tinyAMD1 to you if you just want to repeatedly run runs.

##### **Chrism** [[00:13:16](https://www.youtube.com/watch?v=IAbOilYNLdc&t=796)]
OK.

##### **Geohot** [[00:13:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=797)]
I think that's about my training for now.

##### **Chenyu** [[00:13:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=802)]
Next. So I'm going to go ahead and do some assembly stuff.

##### **Geohot** [[00:13:26](https://www.youtube.com/watch?v=IAbOilYNLdc&t=806)]
Yeah, so I got the emulator finally works. The speed is decent. If you see, I have a pull request to set Python remu to 1 as the default. And I mean, the emulator was great because I found every last little bug. I mean, OK, there's probably still way more bugs. But because it's all tightly integrated, because the DSL and the instruction stuff is all tightly integrated with it, I can do it with the emulator. If there's bugs in one thing, it's easy to find them. So yeah, I have the emulator working for pretty much everything. I think it has more support than remu for re-instructions. It's mostly working on RDNA 4 as well. CDNA is weirder, always. The CDNA-SQGD stuff is weirder, too. Yeah. So I think that's it. Yeah, we're on track for what I said in my sprinkles. I'm going to spend most of the week just cleaning up the cloud-generated code, which I don't know. Again, I have mixed thoughts on it. This is the first time I really tried to aggressively use it for stuff. Everything tiny grad, I ended up doing it by hand. But it is good when I have a test suite, just getting it to pass. And I have a great test suite, too, in extra AMD assembly test hardware, which tests all these weird edge cases of RDNA 3. So yeah. I think I'm just going to clean that up this week, get that merged. I'll at least have RDNA 4 support in the emulator. I have RDNA 4 support for sqgt, mostly.

##### **Geohot** [[00:15:19](https://www.youtube.com/watch?v=IAbOilYNLdc&t=919)]
So yeah, I think it's going pretty well. Hopefully, the rest of the day is going to be good. I think the DSL is fun to program in. Oh, I'm reading the .. I think it's a little unergonomic to do labels and stuff.

##### **Qazalin** [[00:15:51](https://www.youtube.com/watch?v=IAbOilYNLdc&t=951)]
But I think those can be fixed at a higher level.

##### **Geohot** [[00:15:54](https://www.youtube.com/watch?v=IAbOilYNLdc&t=954)]
Yeah. I mean, the problem with labels is they're not per instruction. So I don't know if we want to have a builder class or how that's really going to work. But it's not like I can do anything with labels that are in instruction, right? A label doesn't actually compile to anything.

##### **Geohot** [[00:16:10](https://www.youtube.com/watch?v=IAbOilYNLdc&t=970)]
Yeah, I think, yeah. And some ergonomics would be nice.

##### **Qazalin** [[00:16:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=977)]
And then that's Python. Like, you saw my gem, right? It's a dictionary. It's so fun. It's a little bit more portable, details.

##### **Geohot** [[00:16:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=985)]
Yeah, yeah. That's pretty nice. Yeah, for the outer builder, I mean, it's always unclear. Do you want a builder class? Do you just want a list of instructions and then some transformation function? I lean more toward that.

##### **Geohot** [[00:16:55](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1015)]
Yeah, that's pretty cool.

##### **Geohot** [[00:16:56](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1016)]
I'm thinking about how to start on an assembly outputting back end. It's so nice when you actually output assembly that you get control over what's going on. I found out why Winograd, like Winograd always would crash things. And I finally found out why. It's because it uses Scratch.

##### **Chrism** [[00:17:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1041)]
Oh.

##### **Geohot** [[00:17:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1042)]
There's only a few kernel that are running Scratch. There's only a few kernels that we make that actually use Scratch. Scratch is this special spillover area on RDNA 3. The diversity of instructions that LLVM can output is very high. And you can use all these weird features that you can use. But yeah, you should never actually be using Scratch. If you have a kernel that somehow uses Scratch, you've made a mistake because that kernel will never ever be fast. So yeah, we should be able to build an RDNA 3 back end. On top of the assembly stuff. And then I also want to play with the UOP, with the Asm.matmall, and see if I can get warp specialization

##### **Geohot** [[00:18:03](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1083)]
and see if I can get a 60 teraflop matmall from the 900xdx.

##### **Chenyu** [[00:18:19](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1099)]
You also changed some of the D type stuff. Anything? That people should be aware of?

##### **Geohot** [[00:18:26](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1106)]
Yes, I made two changes. One was int64 promotes to uint64. But 64 can still promote to the float. I think that's fine. It's just annoying when you have an int64 plus a uint64 for that to become a tiny float. That's pretty unexpected. Then I also added a class. I don't love this. But I added a class called const float that inherits from float to deal with the 0 and negative 0 issue. Currently, if you pass 0 and negative 0, any cache in Python will map those two things to the same thing because they're equal. They also hash to the same value. So yeah, I mean, you know.

##### **Chenyu** [[00:19:16](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1156)]
Yeah, we got a new warning for that. I don't know if it's real.

##### **Geohot** [[00:19:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1162)]
Yeah, I saw the warning. I mean, I can fix that. That's just the uop float method checking if it's a const float and returning the arg. I mean, you can return arg.val instead if you want. But I don't know. I'll think about that class more tomorrow.

##### **Chrism** [[00:19:36](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1176)]
OK.

##### **Geohot** [[00:19:42](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1182)]
I fixed a few bugs too. I fixed a few bugs in the defectorizer. I fixed one today in the.

##### **Geohot** [[00:19:51](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1191)]
OK. I fixed one today in the square gate folder thing.

##### **Chrism** [[00:19:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1197)]
OK.

##### **Chenyu** [[00:20:03](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1203)]
I remember there was some discrepancy for our decomposition for log x or sign.

##### **Geohot** [[00:20:12](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1212)]
Oh, yeah. So they're not perfect.

##### **Chenyu** [[00:20:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1214)]
Can I test that already? Or how do I run this?

##### **Geohot** [[00:20:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1217)]
I can write some. I can write some test cases that compare to exactly the value from. You can just compare it to exactly the value in Python. But the value from Python exactly matches the value of the GPU. But I think I'll write some test cases for that.

##### **Chenyu** [[00:20:33](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1233)]
Yeah, exactly call because there are different D type, right?

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1237)]
Yeah, I know what you know. I can write some test case for that. OK. Because our decomposition should be perfect. Oh, also, you can run. So I have an emu2 backend flag to have the emulator use LLVM as a backend. So the way the emulator works is it compiles the instructions to uops. And I have a flag to use the LLVM backend instead of the clang backend. But the LLVM backend has some subtle bugs. And it's interesting. You can see them around the edges. Like fast math kind of stuff.

##### **Chenyu** [[00:21:09](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1269)]
I think some of it is probably the flag we use in LLVM instruction. There's at least one that's buggy.

##### **Geohot** [[00:21:19](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1279)]
Yeah. So one of it is the flag and one of it is the ..

##### **Chenyu** [[00:21:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1282)]
The way we use those flags is we promise the input won't have certain inputs. I'm pretty sure they just use that to rewrite. And in a case that we do use those inputs, it's probably bad.

##### **Geohot** [[00:21:34](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1294)]
Yeah. We have another bug where our decomposition for square root uses pow times 0.5. And this doesn't preserve the sign of the square root of negative 0.

##### **Geohot** [[00:21:50](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1310)]
So we can just bet for negative 0.

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1312)]
Again, I don't know how much we should care about matching the stack. But I think we probably should.

##### **Chenyu** [[00:21:59](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1319)]
I think this is good. Yeah. I think it's good to know the issues. I think negative 0 is more fundamental. NANDs are really nasty. Yeah. And there are backends like WebGPU. It doesn't even support the IE standard. Yeah.

##### **Geohot** [[00:22:27](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1347)]
OK. Good. Next, drivers. Yeah.

##### **Nimlgen** [[00:22:40](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1360)]
So I merged the PMA, so-called test-qtt file. And I don't know exactly which one that is. It's a little bit like an R&V. So it works on 1,490, I think, on the whole Ada generation. So I also have the infrastructure for decoder. And I have some decoder. But it's still not passing the whole test. So yeah.

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1391)]
Well, yeah. No. Great work getting that working.

##### **Nimlgen** [[00:23:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1401)]
So it actually, like for each instruction, it shows the reason why it was told and why it was not scheduled. So that's the whole information. But I think this, combined with the NVIDIA architecture, like that they don't have hardware dependencies, they sold them in software, so I think there should be enough information.

##### **Geohot** [[00:23:52](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1432)]
Are we calling into some library or are we getting the raw bytes out of the GPU?

##### **Nimlgen** [[00:24:00](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1440)]
Yeah, we're getting the raw bytes from the GPU.

##### **Geohot** [[00:24:05](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1445)]
And they're documented somewhere or it's easy enough to just decode them?

##### **Nimlgen** [[00:24:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1451)]
No. Actually, I don't know. Actually, I'm just trying to mean cloud it to reverse that and just to match QPTI. But yeah, actually, I mean, format is pretty simple. Like the buckets are pretty simple there. The only problem is that the only problem I still have is like matching each sample to the correct PC address. That's like the only issue.

##### **Geohot** [[00:24:41](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1481)]
Yeah. So I mean, the way to do that is just to like dump them.

##### **Geohot** [[00:24:48](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1488)]
The instructions all issue in order. It's all in order. Actually, I think the issue.

##### **Nimlgen** [[00:25:03](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1503)]
Yeah, I mean, the issue I have is that I think it's just somehow mixture like different different things. So for example, something like something at something, but just山 pass in between like X or something. Was it compete with load report or... But like some of the sc jurisprudence is the same or do you need to save it in the new шейAccess frame? No, just deploy it. And login or I can't, like, we usually you know, we just need to access Bosch際 aspect address, so you need it.

##### **Geohot** [[00:25:38](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1538)]
unusualudo.org.

##### **Chrism** [[00:25:39](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1539)]
Yeah, yeah.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1548)]
So, no, I mean, probably...

##### **Nimlgen** [[00:25:51](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1551)]
I don't know. Actually, about waves, I also don't know. I definitely know how to find the correct SMID, TCPND, and all these things, but I'm not sure about waves either. So, yeah.

##### **Geohot** [[00:26:10](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1570)]
What SQTT has is SQTT, it's all, like, the SMs are all completely separate. What SQTT has is a packet that tells you what wave did the issue. I'd be surprised if they mixed SMs, because I'm just trying to think about how they actually

##### **Geohot** [[00:26:36](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1596)]
build that in hardware. Maybe.

##### **Nimlgen** [[00:26:49](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1609)]
So, yeah, I mean, yeah, actually, for 5090, it kind of works. I mean, a bit different registers. They're not well documented. I just get some of them. But I think with... 5090, I'll refactor this, and it will be a bit better than it's now.

##### **Geohot** [[00:27:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1637)]
The other direction I kind of wanted to talk about with drivers was getting... Being able to quickly halt kernels and making sure that if a kernel does crash, it doesn't

##### **Geohot** [[00:27:32](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1652)]
bring the whole GPU down. Right now, I'm not even sure what I'm doing.

##### **Geohot** [[00:27:42](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1662)]
But right now, if I write a bad kernel on my laptop, it will be okay until I kill the Python process. Then once I kill the Python process, my screen turns off, and it comes back about half the

##### **Geohot** [[00:27:54](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1674)]
time. I wonder if there's some, like, interrupt that we're not clearing.

##### **Chrism** [[00:28:05](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1685)]
I don't know. I don't know.

##### **Geohot** [[00:28:10](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1690)]
I don't think so. I mean... Yeah, actually, I tried to...

##### **Nimlgen** [[00:28:18](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1698)]
So I've tried to, like, interrupt kernel. I mean, that's, like, the first thing. Like, to interrupt kernels, the issue is that actually there is a special SKU comment that you actually can send to the... Um... Like, to the exec. Yes. execution unit, but I don't know, it doesn't work for me, surprisingly. I mean, it does nothing. Actually, it's just still executing all waves as usual. And the second thing is your potential. It's also fast. You can completely dequeue the queue and create a new one in the same place. The only issue is that it actually works on, like, but we have issues with AQL and MI300, MI350, because, like, after the queue recreation, I mean, there is something you need to touch and I don't know what, actually to make the XCCs sync again, because it won't sync them. And they have, like, mdgp has the same problem if you run with, like, if you manually assign queues if it's not mass analog. So they have the same problem. So I don't know. I mean, there's definitely a bit more investigation needed to do, but I don't know. If there is any register, it's not documented. Like, it's not in the headers.

##### **Geohot** [[00:30:03](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1803)]
Have you looked at how you amass the queue? How MR does this and how, like, GDB does this? The tpus have, like, full debuggers where you can go and, like, single step through things and

##### **Nimlgen** [[00:30:19](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1819)]
Yeah, actually, you can do... Or how it works but... ..using this asaturatooncmd, there's basically different comments included, like, the trap so you can just do single. You can set breakpoints using this. I know. Yeah, I'll try that, but I know. Like, the kill command does nothing for me.

##### **Geohot** [[00:30:45](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1845)]
And then what about those sq interrupts?

##### **Nimlgen** [[00:30:50](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1850)]
Yeah, actually, I've added these, so it's already merged. Yeah, actually, it's printing everything right now, but I will... I mean, everything, almost all of them are fatal with some issues with the GPU, so yeah, I think...

##### **Geohot** [[00:31:13](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1873)]
It's just a lot better if it's not hanging for the full 30 seconds.

##### **Nimlgen** [[00:31:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1877)]
Yeah, yeah, I mean, I'll plug them in, so yeah.

##### **Geohot** [[00:31:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1882)]
Yeah, great. I can write a... Okay, so look, Yeah, great. I can write a... Okay, so look, Tesla needs to...

##### **Geohot** [[00:31:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1885)]
I need to write. I'm gonna write this on my board. I need to write the decomp tests.

##### **Geohot** [[00:31:34](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1894)]
I need to write tests for GPU crashes. And my expectation is that they don't bring the whole GPU down, and that they don't wait 30 seconds. And I also need to work on embedding

##### **Geohot** [[00:31:51](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1911)]
on an MI350X. Yeah, so my expectation is that these tests will not bring the whole GPU down. Right now, that's what they seem to do. And then it needs to require... And then we need to reset. Yeah, yeah.

##### **Geohot** [[00:32:13](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1933)]
I don't know if they're all sq interrupts. There's a bunch of different ways you can do it. There's out-of-bounds memory accesses. There's...

##### **Chrism** [[00:32:24](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1944)]
No, I don't know.

##### **Nimlgen** [[00:32:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1945)]
No, actually, we, like, currently, we have the interrupt handler, and we currently get all interrupts there, and I just print all of them, including this data fabric, including the page files, sq interrupts.

##### **Geohot** [[00:32:41](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1961)]
Yeah, I just...

##### **Chrism** [[00:32:43](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1963)]
Yeah.

##### **Geohot** [[00:32:45](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1965)]
I'm also kind of curious with the other emulators if we can have a way to single-step through the GPU.

##### **Chrism** [[00:32:50](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1970)]
Yeah, sure. I don't know if we can do that.

##### **Geohot** [[00:32:55](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1975)]
Like have a single step and dump the state of every step. You mean through the kernels, yeah?

##### **Geohot** [[00:33:04](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1984)]
Yeah, yeah, like if I can like somehow run a kernel in some... I wonder if I like, how is the debugger working? It's using these SQ commands?

##### **Nimlgen** [[00:33:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1994)]
Yeah, yeah.

##### **Geohot** [[00:33:16](https://www.youtube.com/watch?v=IAbOilYNLdc&t=1996)]
You can set different breakpoints there using these commands. What might I search for to find one of these? SQ underscore CMD, so in the kernel. In the Linux kernel? Yeah. Go work on the other videos though. I have a 5060 here.

##### **Nimlgen** [[00:33:52](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2032)]
Yeah, it's actually for Apple. Actually, it got approved. The only issue is with entitlements. So I don't know actually what they granted to us. The issue is that like the kernel does not accept the entitlement they just gave us because they actually gave us the integer number and they expect a mask there. So it doesn't even work without zip.

##### **Geohot** [[00:34:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2062)]
Why? I mean...

##### **Nimlgen** [[00:34:30](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2070)]
So the issue is that we add entitlements to our text. Yeah, yeah, sure. Yeah, they also gave us like the provision and profile which is signed by Apple and so actually they allow us to use the entitlement which is like integer and it's like the AMD number. Yeah. And the issue is that this format seems to be not correct because kernel doesn't accept it. Oh, so we need... Like, it accepts mask. Yeah, actually I asked them two business days on the clarification about the format.

##### **Geohot** [[00:35:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2114)]
Great. Yeah, I mean I tried resubmitting it with the AMD and the NVIDIA thing. It looks like it just wants you to type a number into a box. I mean you're logged into my account if you need to pay again I can do it um yeah I think I think we should make slow and steady effort on this it's super annoying that they baked the number into the provisioning profile yeah I saw that there and I was worried about that yeah but yeah yeah stay on top of it just just keep pushing them a little bit if we get it in like a month a hardware is not ready yet anyway but we're gonna get two in the mail soon the comma chestnut I'm getting two comma boards in the mail with the SM chip on them and they had

##### **Wozeparrot** [[00:36:04](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2164)]
those for a bit and I'm unable to get it to reliably link at USB 4 oh oh good I'm

##### **Geohot** [[00:36:10](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2170)]
glad you're testing them yeah complain to Robo about this okay but I did the

##### **Wozeparrot** [[00:36:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2177)]
mod that he suggested and they still like crash out oh

##### **Chrism** [[00:36:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2181)]
yeah I'm glad you're testing that yeah complain to Robo about this okay but I did the mod that he suggested and they still like crash out

##### **Geohot** [[00:36:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2182)]
after a bit yeah yeah um mention this to a deep also a deep will uh yeah well we'll stay on top of us for us before is a really high-speed signal that's like hard to route and stuff never tuning , anything else for drivers

##### **Nimlgen** [[00:36:56](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2216)]
um no but actually I think full armor I think we want to include the all-to-all flag so it's a bit faster with it

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2226)]
oh cool oh you have a you have a flag after the training yeah just add that to Dev run okay yeah I like to Dev raw and also post in the channel okay yeah great yeah that's good uh next for the viz fast jam

##### **Qazalin** [[00:37:28](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2248)]
yeah it switched with to all RDSL so no LV I mean AMD disassemble or the CFC graphs and stuff

##### **Geohot** [[00:37:39](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2259)]
with our stuff

##### **Qazalin** [[00:37:44](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2264)]
I'll redo the sort of cleanup of the sqtt and the RDSL stuff will be done in the next few weeks so yeah I think that's good the thing I think about is that the rdmi4 is merged is not perfectly correct there's still some yeah issues uh I'll work on the tests and cleaning up that code and

##### **Geohot** [[00:38:02](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2282)]
I have it on my desk so I can test it every day so it's fixed um yeah we need that that in enum seems totally different for rdmi4 and for cdna we don't have a hope

##### **Geohot** [[00:38:27](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2307)]
no I can talk about cdna but I'm looking now I'm looking now at viz so this is not this is not LLVM so these things are just uh like our our output

##### **Qazalin** [[00:38:37](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2317)]
no LLVM ever

##### **Geohot** [[00:38:38](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2318)]
yeah but you're not even using my disasm

##### **Geohot** [[00:38:44](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2324)]
I'm using your disasm yeah if this is from disasm then where are the commas uh

##### **Qazalin** [[00:38:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2333)]
so if you do g you'll see the dis the sasn if you see the graph it's the operand and the wrapper of those operands

##### **Geohot** [[00:39:06](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2346)]
oh got it

##### **Qazalin** [[00:39:07](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2347)]
oh cool yeah

##### **Geohot** [[00:39:09](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2349)]
yeah okay good this is Rita.S", yeah I think this has been nice I think it's like great pretty readable

##### **Chrism** [[00:39:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2354)]
yeah

##### **Geohot** [[00:39:15](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2355)]
our mosaics would again sqt graph to uh that'll take a lot longer, so that kind of thing

##### **Geohot** [[00:39:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2361)]
No, it's fine in the graph map to have them. Cool, yeah, so rdna4sqtt, if you want to clean up sqtt,

##### **Geohot** [[00:39:35](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2375)]
that file that's in there,

##### **Geohot** [[00:39:40](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2380)]
the sqtt-lib or whatever it is.

##### **Qazalin** [[00:39:43](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2383)]
Oh yeah, sqtt-map. I did attempt to merge the... the RockProp stuff with the examples, or redo that patch, I don't know what that was.

##### **Geohot** [[00:39:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2397)]
Yeah, yeah, I mean, you removed... you used your RockProp stuff, which is LLVM, and that, like, crashed on my computer, and if you don't put the right thing into RockProp, it crashes.

##### **Geohot** [[00:40:09](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2409)]
See?

##### **Geohot** [[00:40:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2411)]
Oh, good, I like that there's delimiters now between the... when I zoom in on something, I can see how many there are. The little gray boxes.

##### **Geohot** [[00:40:20](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2420)]
Oh yeah, I added that on the lines. Cool. Between the ways. So how close are we... Oh, the instructions here. Oh yeah. I see. But where is that instruction in, like, context? What do you mean? Well...

##### **Qazalin** [[00:40:47](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2447)]
Oh, I see. You mean the line number. Right, the... Yeah.

##### **Geohot** [[00:40:52](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2452)]
Yeah, I mean, kind of what I'm imagining is, like, on that right thing, instead of just printing the one instruction, imagine it shows, like, all the instructions before, and then all the instructions after, and then just has that one lit up. Not all, but, like, maybe, like, you know, 20 before and 20 after, and includes the offset into the kernel.

##### **Geohot** [[00:41:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2471)]
Oh, nice. Yeah.

##### **Geohot** [[00:41:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2474)]
But now when I click... Now, when I click the VALU, I want it to draw a line back to the NQ.

##### **Geohot** [[00:41:27](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2487)]
We still don't know for the VALUs

##### **Geohot** [[00:41:29](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2489)]
which one corresponds to the instruction. It's just the ones on the left.

##### **Geohot** [[00:41:33](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2493)]
We do not, yeah.

##### **Geohot** [[00:41:36](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2496)]
And then also, I think left and right arrows should jump between instructions.

##### **Geohot** [[00:41:44](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2504)]
Jump between instructions in the... In the wave. Wave. If you're not in the wave. Then they don't have to do anything. I don't know. I think, like, it just...

##### **Geohot** [[00:41:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2517)]
On the ALU, it can just move on the ALU. Okay, so we still got to link the ALU ones back to the wave. Yeah. Finish the RDNA for sqgt stuff.

##### **Geohot** [[00:42:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2531)]
Did you see what I had for cDNA? I didn't read the diff.

##### **Qazalin** [[00:42:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2537)]
It sounds like it's different. And weird. And RockProf does weird shit.

##### **Geohot** [[00:42:24](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2544)]
Well, yeah, RockProf does weird shit. Yeah, they... I can't get the times to match exactly. And what Claude is saying is that RockProf is, like, doing a whole lot of number fudging to kind of get things to match. So I don't think we're going to have exact match tests for it. The other thing that's annoying about it is... It doesn't have... So the RDNA sqgt has a, like, a long delay op. The cDNA one doesn't have a long delay op. It just has these absolute timestamps, and then it, like, resets it to the absolute time. But I think what we have is probably... Like, I found the ALU in the exact, so it's probably already good enough to visualize. And then hopefully, it's not going to be a problem. But in the visualization, we can kind of see what's going on. I just need to look at a lot more kernels. Or, I don't know, if you want to own this project,

##### **Geohot** [[00:43:29](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2609)]
do RDNA4 and then do cDNA. I'll take that. And then how about the gem? Gem. I have the... Square one in RDSL. It works nicely. Yeah, but... I have, like, a... Lama's not square.

##### **Qazalin** [[00:43:58](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2638)]
It's a square. It's a square. I'll get the... I know that now we are working towards Lama, so I'll have the... Just Lama script. I think there's, like, two different gems.

##### **Geohot** [[00:44:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2651)]
Is Lama a square? I don't think it's a square. No, no, no. Lama's not square. Yeah, it's not square.

##### **Geohot** [[00:44:17](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2657)]
Yeah.

##### **Geohot** [[00:44:18](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2658)]
It's not square.

##### **Geohot** [[00:44:19](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2659)]
Yeah, just find the gems in Lama. Test on the gems in Lama. Let's get those fast, working for both 300x and 350x.

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2670)]
Yeah, sounds good. I just think this doesn't... Okay, it would be great if we could... have something merged by the end of the spring. I'll try. I mean, like... Yeah, I throw it to Cloud, and it's like...

##### **Chenyu** [[00:44:51](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2691)]
You mentioned that there was a JIT issue with the custom gem.

##### **Geohot** [[00:44:59](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2699)]
Is that still a thing? No, there's different issues now.

##### **Qazalin** [[00:45:08](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2708)]
Every time I remove some complexity... So the problem is that the kernels are very complex, the kernels that Torch outputs. They're like... More than 20,000 lines of instructions. So I walked Cloud through using SQTT to trace the instruction path for the reference MNKs and sort of go through and find the branches that are actually needed. I fixed one of those JIT problems by just removing a bunch of crap from the kernel that I'm pretty sure caused... caused this race conditions.

##### **Geohot** [[00:45:49](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2749)]
Yeah, this just sounds like it's not going to work. I think this whole approach... I was shocked. So that whole AMD as a map model... Cloud... Cloud can't write assembly code. Like, it just sits there and tries for 20 minutes and it breaks things. And it's just like things that are obvious when you look at it. I don't know what's wrong with it and why it can't do it. So I don't think that approach... is really going to work. I think... Do we have another place we could... Like, how clean are the gems that are outputted from Mojo?

##### **Qazalin** [[00:46:26](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2786)]
I haven't looked at it. Torch is very unclean. Torch takes a lot of Cloud hour... Cloud minutes to get cleaned up.

##### **Geohot** [[00:46:37](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2797)]
I'm almost wondering if we can support Mojo. If we can just, like, pass the Mojo kernel in. Even if we have to use Mojo to, like, to, like, size specialize them. Like, in Mojo backend or... Just get the kernels in? Put the kernels in? Just get the kernels, put the kernels in.

##### **Geohot** [[00:47:06](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2826)]
Even without, like, having to put them in our assembly or anything. Just, like, dump the blob and shove the blob in. Dump the machine code blob out of Mojo. Or anything. Even if it's the machine code blob from Torch. It doesn't really matter where it comes from.

##### **Qazalin** [[00:47:23](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2843)]
Yeah, dump the machine code... It's not really... Like, you have to tweak the arcs a little bit to work nicely with our buffers.

##### **Geohot** [[00:47:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2851)]
But... Other than that, it's good. Yeah. And then in Mojo, we can also, like, change it. Or change the arcs. Cool, yeah. That's some kind of fast... Yeah. Some kind of fast gem in there. Continue with the viz improvements. SQTT for our Unicorn CDNA. Yeah, also have the MMA peak stuff.

##### **Qazalin** [[00:48:05](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2885)]
I did switch MMA peak from string formatting to actual DSL usage. So we do all the... We do all the...

##### **Chrism** [[00:48:15](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2895)]
We do all the...

##### **Qazalin** [[00:48:16](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2896)]
We pack the bytes ourselves. LLVM still does the ELF. The ELF PR is ready. It's very mechanical. But I think after that, we're just done with LLVM. But maybe we'll have a full stack ourselves.

##### **Geohot** [[00:48:35](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2915)]
Yeah, great. I mean, I don't know. It's like template things are annoying. I've always hated how you have to, like, put the thing in YAML and then LVM parses the YAML and stuff. Like, why am I doing this? These are real bytes from this thing.

##### **Geohot** [[00:48:48](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2928)]
So yeah, I think the ELF PR is good too. Yeah, I think there's like a bunch of tooling that we need to do around the DSL to make it usable.

##### **Chrism** [[00:49:05](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2945)]
So...

##### **Geohot** [[00:49:08](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2948)]
I mean, yeah, if you just mean the branch thing, the way that I would do that is I would just make a list of the instructions and have some of them. I would put some, like, tokens in that list and then have one function that goes in and fixes that up.

##### **Geohot** [[00:49:21](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2961)]
Like branch fixup. I can clean up how it's done and...

##### **Geohot** [[00:49:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2971)]
Actually, you know what? Merge the ELF stuff and then I'll switch over. I'll add to my list for you this week. Use an AMD as a map model with a nice abstraction for that.

##### **Geohot** [[00:49:46](https://www.youtube.com/watch?v=IAbOilYNLdc&t=2986)]
That sounds good? Yeah. All the ELF. All right. And thanks for pushing on making the imports fast. Very nice. I just realized how nice it is. It's so nice when you run a test and it's like really fast.

##### **Qazalin** [[00:50:09](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3009)]
It's so noticeable for CLIs.

##### **Geohot** [[00:50:13](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3013)]
Yeah. Just... Yeah.

##### **Chrism** [[00:50:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3014)]
Yeah.

##### **Geohot** [[00:50:18](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3018)]
Can I go see? Anything else? That's all.

##### **Chrism** [[00:50:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3031)]
Okay.

##### **Geohot** [[00:50:34](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3034)]
Next is my stuff.

##### **Chenyu** [[00:50:37](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3037)]
For JIT, I think I did everything I wanted. So I went through the process. I went through the open issues and close. I think pretty much all of it. Let's go to JIT. The most notable change is now JIT will assert if you try to access the underlying underscore buffer. So if you call like item or to list or things like that in a JIT function, it will erase. Because the behavior is it would read whatever that value is and it won't read again or the replay runs. Now if you look at the test underscore JIT underscore foot guns, the only thing that's two main things remain and one is assigned related and that's just the issue with assign. Another is we reuse the output buffer and that's a choice I assume compared to always making a copy to that buffer.

##### **Geohot** [[00:51:40](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3100)]
I think that we should always make the copy. And then... And then have a flag to a JIT that disables a copy.

##### **Geohot** [[00:51:47](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3107)]
Is that true?

##### **Geohot** [[00:51:50](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3110)]
I don't think so. I think that that's one of the like one of the big unintuitive things.

##### **Chenyu** [[00:51:55](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3115)]
So this I guess I guess two things that's a choice. Another is for symbolic shape. We don't correct and rewrite the shape after we do after the JIT run. But that rewrite is on the hot path. And I don't really feel like that's important.

##### **Geohot** [[00:52:15](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3135)]
Very similar to the copy trade off. Wait, sorry, say that again.

##### **Chenyu** [[00:52:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3145)]
So if you create, say you do the KV cache appending and we return KV cache and what's the size of like, basically what's the variable that's bind to that variable? The actual variable. It should increase by one every round, right? But for now, it's whatever the capture value is because we never update the actual value. Let's let us, I don't know, that's on the hot path. I really don't want to add the rewrite layer.

##### **Geohot** [[00:52:58](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3178)]
Yeah, it seems that seems fine. Yeah.

##### **Chenyu** [[00:53:02](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3182)]
So, okay, I would check the copy thing.

##### **Geohot** [[00:53:07](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3187)]
Maybe that's fine. The other thing. I think I'm going to add the Can we remove realize from set item? Yes, that's the next thing. Great. I would be so happy if realize just removed from set item.

##### **Chenyu** [[00:53:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3205)]
Yeah. So the main issue is with assign and specifically set item when it's slice. So I'm working through the assign cases now. By reading the current assign special handling, I can find more wrong cases. So I have, I just merge more stuff that is wrong. Probably I will spend this week to see what I can do here. I think the goal is it shouldn't, everything should be lazy and the scope of assign and things it affects would be updated correctly. Now we have two issues. One is the kernel we generate has the data race issue or the data itself is wrong. Then at higher level at tensor level or tensor and scheduler level, the kernels that needs to be updated is wrong. And that's the reason why we need realize at various place to inform the scheduler. You also need to update this kernel. We have bugs in both places. And I will fix the lower one first because the kernel we generated shouldn't ever be like wrong. That's the issue that sometimes we have crash on like certain backend, I believe.

##### **Geohot** [[00:54:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3293)]
Yeah.

##### **Geohot** [[00:54:54](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3294)]
So we have a thing to fix this. I think it was a thing in the schedule they fixed at this. Maybe it doesn't work.

##### **Chenyu** [[00:55:01](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3301)]
So pretty much all the spatial case we handle just work sometimes and more like a hack. And that's the unfortunate part.

##### **Geohot** [[00:55:13](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3313)]
Yeah. I mean, I think we also need to like, I have a spec, but I think it should all be lazy. And like, yeah, sign should be an op.

##### **Chenyu** [[00:55:20](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3320)]
I think everything should be lazy, but the output follows the eager output. That's my working principle on these things.

##### **Geohot** [[00:55:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3331)]
Yeah. I remember sitting in Hong Kong doing some of these on the board. But yeah, if you have like a good principle, you can do it. I think it's a good principle to figure out what these cases are. And I'm always a fan of just asserting in ambiguous cases and being like, don't write it this way.

##### **Chenyu** [[00:55:47](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3347)]
Yeah, that's fine.

##### **Geohot** [[00:55:50](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3350)]
But yeah, I hit the set item realized thing. I was trying to debug some kernels. And I'm like, why is this kernel empty? Why all it's realizing? Yes.

##### **Chenyu** [[00:56:00](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3360)]
So for the realized cases, almost always because our capture of scope is wrong. So the things that needs to be updated is not updated.

##### **SPEAKER_07** [[00:56:09](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3369)]
Yeah.

##### **Chenyu** [[00:56:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3371)]
Yeah. Other minor thing, mypy and type equals to 1. Not very important. It's very annoying. So last week, I mentioned this invalid in different layers. Invalid should only be in len. It's even more annoying because for all the tensored math mixing, it can actually take you up because we also support let. Yeah. It's all a symbolic tensor case.

##### **Geohot** [[00:56:42](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3402)]
Well, yeah, but that should be wrapped.

##### **Chenyu** [[00:56:45](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3405)]
Wrapped by what?

##### **Geohot** [[00:56:47](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3407)]
Tensor. You can't just do like a tensor plus a uof. That shouldn't be allowed. But if that is allowed, it shouldn't be. No, no.

##### **Chenyu** [[00:57:02](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3422)]
So I think what's wrong is with the way we write. You fix and try to normalize that.

##### **Geohot** [[00:57:08](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3428)]
There may very well be a bug, but the intended behavior is that you can wrap a uof with a tensor. So you can call tensor uof and that creates a tensor that's backed by that uof and that's totally fine. But you can't do tensor plus uof. That shouldn't be allowed.

##### **Chenyu** [[00:57:27](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3447)]
That makes sense. I hit something else. I don't think I remember. Yeah. But let's slide it. I don't think I remember. So now my focus on let is more if there is something that's definitely wrong, we need to fix that. So for example, I merged the other thing that's a mesh grid thing. Mesh grid can take string, whatever string. So things like let we need to fix.

##### **Geohot** [[00:57:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3473)]
Oh, you merged the mesh grid can take string? Why were the literals not correct?

##### **Chenyu** [[00:57:58](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3478)]
Because you can pass whatever string to it. We use let in test. Oh, I didn't realize that. I commented on let . I think I'm pretty sure the author is not aware of the full ramification of the change, but that's correct.

##### **Geohot** [[00:58:14](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3494)]
Right. Yeah, I just looked at it. I was like, this is a repair. But cool. Yeah, I was also thinking more about the type thing, the invalid thing. You sure you don't want to put invalid in const type?

##### **Chenyu** [[00:58:28](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3508)]
There are other issues to let.

##### **Geohot** [[00:58:31](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3511)]
Yeah. Like the annoying. Like what? Because I was thinking about this more.

##### **Chenyu** [[00:58:41](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3521)]
I cannot remember. There's one thing that's annoying.

##### **Geohot** [[00:58:44](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3524)]
I remember we brought it up last week, and I thought about it a bit more. And I'm like, I think we do want invalid in const type.

##### **Chenyu** [[00:58:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3533)]
OK, I was thinking about this more. I cannot remember. There was some random mypy type rabbit hole. So one last thing, just quick mention. I tried to do something with the wear closure thing, but speed is not ideal. But also, I want the more powerful version of what I did. So I ended up just commenting that out, and we'll revisit later.

##### **Geohot** [[00:59:19](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3559)]
Yeah, so I thought about it quite a bit. The problem is anything that uses topo sort, or any form of topo sort, backward from slice, is going to be n squared if you have a whole lot of wears. So imagine your kernel is just all wears.

##### **Chenyu** [[00:59:38](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3578)]
Yeah, so the real use case for that is really just you top down and you do it once. Then it should be done. There shouldn't be like recursive effect on this thing, because your closure can only be refined one way. Yeah. So because of that, I want to... It's also not that important. Most of it is simplifying some small stuff. But in principle, we just don't have a good way to represent this more refined and refined closure. And now we kind of brute force everything, see if they match. So my plan is I will think about this slightly more and find a concrete case we want to improve. Otherwise, comment it for now is fine.

##### **Geohot** [[01:00:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3625)]
Well, I can give you an O of n way to write that. What you can do...

##### **Chenyu** [[01:00:29](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3629)]
I don't like that. I feel that's too specific to wear.

##### **Geohot** [[01:00:33](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3633)]
Oh. I mean, you can add a recursive property to uop that says, like, basically gates. Like parent gates. It'll return to you an empty parent.

##### **Chenyu** [[01:00:45](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3645)]
If we go down that route, I would just want more things like a wear, and you just log more metadata to the node to make it fast. But then it's too complicated to maintain and things like that.

##### **Geohot** [[01:00:57](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3657)]
I think this is complicated. Just one decorator with recursive property.

##### **Chenyu** [[01:01:03](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3663)]
Yes, it's a decorator and has a name recursive in it. It's already complicated. Yeah, yeah.

##### **Geohot** [[01:01:08](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3668)]
I think this is fine. I actually think this is fine.

##### **Chenyu** [[01:01:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3671)]
My point is if I find a good use case for this, then I will pursue more. For now, the thing is simplifies. It's rather trivial, so I don't think it's worth it.

##### **Geohot** [[01:01:24](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3684)]
Sure. But yeah, I'm saying if you do want to write it, recurve it. But the recursive property is not the end of the world. It looks like ranges.

##### **Chenyu** [[01:01:32](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3692)]
And we also don't have test, let guards list. So maybe that's another way to think of all this, like what behaviors we don't want it to have.

##### **Geohot** [[01:01:41](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3701)]
Yeah, yeah, yeah. We don't have good ways of determining the n squared behavior, sure.

##### **Chenyu** [[01:01:46](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3706)]
Yeah. Okay. Anyway. Yeah, that's pretty much my stuff. We go slightly above time already. So Chris.

##### **Chrism** [[01:01:56](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3716)]
Yeah. Yeah. I mean, I'll talk quickly. So I mean, yeah, last week I mostly worked on this decomp stuff. And yeah, so that all works. I think there's a couple edge cases with respect to division for signed longs that I have to just iron out. But other than that, all of the integer operations work. So I just need to iron out the edge cases with the signed longs. And there's a couple things with casts that I have to make sure all that stuff works. But that should all be good. I'm going to try and do that today. Get that merged. The silly thing is that the only thing that this actually affects within the code base where we do isdtype supported for long is the num batches tracked in batch norm, which doesn't actually do anything. The only reason that we include that at all, I think, is for compatibility with PyTorch. Yeah. So in batch norm, it only exists to track the number of what batch you're currently on. There's no value outside of that. It doesn't actually do anything. Well, yeah.

##### **Geohot** [[01:03:09](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3789)]
But I think overall, this has a ton of value. Yeah. Because now you don't need to have a long dtype, and you get long dtype. Yeah. Yeah, for sure. So we have so many skips in all of our tests for WebGPU. And I would love to just start removing these. And I think a good bunch of them are because of the long issue.

##### **Chrism** [[01:03:29](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3809)]
Yeah. The one thing I will say is that the division implementation, I mean, this is always to be expected, is that integer division, like, emulated integer division is always going to be slow. But it's, I mean, it's slow. I'm using a shift and subtract method, which is nice and, like, the code to implement is nice and elegant. But there are definitely faster ways to do it. But the problems they require are a lot of where's.

##### **Geohot** [[01:03:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3833)]
I would not worry about this. I would just get something merged that allows us. So the goal is not to generate great code for this. The goal is to remove, like, remove any special casing upstream. Yeah. The dream of TinyGrad is not that it's going to output great code. There's no point, like, what I always say is optimizations are never worth the tradeoff. Never worth the tradeoff. Yeah. Never worth the tradeoff. But what is worth extra line to the code base is normalizing the higher API layers. Yeah. So the problem with ISD type supported and anything that looks like that is we need to provide the exact same API for tensor on every single device. Yeah. No one's seriously using longs for compute. The only thing people are using longs for is they have one stupid long in their ONNX model. Right? And this is the case in practice. They have one stupid long in their ONNX model, and then that stupid long doesn't let the thing compile for their WebGP. Yep. That's what this is designed to fix. Yep. Also, I mean, the great thing is also we have all the infrastructure to test this and make sure it actually is complete and is capable of doing everything. But yeah, don't worry about the speed. Just worry about the correctness.

##### **Chrism** [[01:05:12](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3912)]
Okay. Sounds good. The other thing that's worth mentioning is that we need to figure out, so for instance, like, the OpenPilot model has halves in it. Yeah. And, like, we have this special case in the Qualcomm compiler where we say, like, oh, the Qualcomm compiler is flaky with half. So we say that DTYPE is not supported for half on Qualcomm. So we need to, like, this is an example of somewhere where we can't just break, we can't just say, like, oh, like, too bad, your device doesn't work because you don't support half. So I think we have to figure out what we want to do about that. I'm not sure what the best solution is. I think the best solution is there for loading an ONNX model for Qualcomm where there's a

##### **Geohot** [[01:05:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3953)]
half. Yeah.

##### **Geohot** [[01:06:00](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3960)]
What I would do there is I would add a rewrite rule that rewrites all halves to floats in the Qualcomm renderer.

##### **Chrism** [[01:06:10](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3970)]
Okay. Wait, there's one. Yeah, well, this is a little bit more complicated, actually, because if you have, like, a buffer in your ONNX model, you need to connect it to the onX model. So if you have a buffer in your onX model, you need to cast it on CPU. So if the buffer contains floats, or sorry, contains halves, you need to be able to rewrite the buffer, like, you need to be able to cast all the contents of the buffer to whatever data type you actually do support. So it can't just be a rewrite rule.

##### **Geohot** [[01:06:35](https://www.youtube.com/watch?v=IAbOilYNLdc&t=3995)]
No, but no, okay, then this can be a rewrite rule. So it can. So here's how you can do it. You can use, again, this is a place where we can, how would you fix this with a decomposition?

##### **Chrism** [[01:06:47](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4007)]
I mean, I guess you would, you would. Yeah, you can do the cast without actual support, right? You can do it with, like, state fiddling. Exactly.

##### **Geohot** [[01:06:56](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4016)]
So yeah, we don't want to see, like, like, think about tiny grad as, like, something that's, like, moving down the stack. I do not want to have any back pressure. Like, like, what you're saying there is like, oh, well, so the Qualcomm thing needs to be able to report to the higher level and say, I don't support half. So therefore, you have to do a cast on the CPU. How do we just? Yeah, implement this with a bunch of pitch shifts.

##### **Chrism** [[01:07:23](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4043)]
Okay.

##### **Geohot** [[01:07:24](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4044)]
Yep.

##### **Chrism** [[01:07:24](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4044)]
That makes sense.

##### **Geohot** [[01:07:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4045)]
Yeah, I mean, it's just, and then it's fundamentally on the Qualcomm compiler. We want to keep this complexity. So ideally, we want a universal decompositions layer that's usable by any renderer to say, basically, look, I don't support that D type. I don't support that kind of cast. I don't support, right? And we have a bunch of ad hoc cases right now that should be cleaned up where, like, I think we have a bunch of, like, hats for B float and stuff. In like AMD where it's like, oh, we don't support B float on this math. That should all be handled at the decompositions layer.

##### **Chrism** [[01:07:58](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4078)]
Yeah. Yeah, that makes sense. That makes sense. Yeah, you're right. That should be simple to do with Bitfitline.

##### **Geohot** [[01:08:04](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4084)]
Yeah, I know this project kind of got added to your sprint, but I think it's super worthwhile and worth doing it well. So I know I said, like, you know, want to get everybody over to Lama as soon as possible. But if this pushes out image D types, another sprint, I think that's okay. As long as it's not a big deal. As long as you do a really nice job on the decomposition.

##### **Chrism** [[01:08:22](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4102)]
Yeah. Yeah. My hope was to try and get all the decomp stuff done last week, but it obviously didn't happen. So I was hoping to get to work on image this week. I'm still hoping that I will get some time to work on image this week, but we'll see.

##### **Geohot** [[01:08:34](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4114)]
Yeah, no, but I definitely want to at least decompositions clean up the sprint. But yeah, the like, my theory about most software is that so much things just exist to support other things. Like the minute you start saying a D. Type cannot be supported. Oh, man, the amount of like, like stuff that you now have in your higher layer is to deal with that fact. If any higher layer ever mentions a device like, oh, unit tests skip on web GPU. Well, yeah, yeah. The promise from tiny graduates users is that no matter where you run this code, it will behave identically. Yeah. Only thing is how fast it is. That's our slogan. Come on, ties the pay to flop. And that's how we're going to sell chips. That's what we're going to sell chips to people. Yeah.

##### **Chrism** [[01:09:25](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4165)]
Yeah. Sorry. One more thing. You know, that was a good note to end on. But is that I think I did notice is that our D type tests are a little bit inadequate. For instance, there was nothing testing negation. So like, for instance, like web GPU just didn't support negation at all. And so this is like, this is something I've noticed is that we need to have better tests for a lot of like, so for instance, D type out. And then we have a lot of like, you know, like, you know, like, you know, like, you know, like ALU that needs to have better tests.

##### **Geohot** [[01:09:53](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4193)]
Great. Have the tests provided. Anything else? No, that's it.

##### **Chenyu** [[01:10:11](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4211)]
I think it's about time, but or do you want to conclude the meeting by saying comments on the test? something on the anthropic challenge?

##### **Geohot** [[01:10:23](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4223)]
Oh yeah, I had a lot of fun with that. It was cool. The guy who wrote it, I had a little Twitter exchange with him. He looked at the TinyGrad code and he's like, oh, that's pretty elegant. Where do you specify the ALU thing? And I showed him the upcast thing. Yeah, but I think it's super good that another person just posted a pull request that even beat my solution using what looks like very clean TinyGrad code. So it's awesome that TinyGrad is capable of outputting state of the art solutions on Anthropix VLIW challenge. I mean, this is how Anthropix is thinking about this stuff. They're thinking about buying those Tranium chips. So yeah, I think it's really good that we have all the right pieces in place.

##### **Geohot** [[01:11:15](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4275)]
And yeah, our own hardware looks closer than ever. We're not here, we still have a lot to do, but it looks closer than ever.

##### **Chenyu** [[01:11:26](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4286)]
Great. Okay, that concludes this meeting. Thank you, everyone. See you next week. Bye-bye.

##### **Geohot** [[01:11:33](https://www.youtube.com/watch?v=IAbOilYNLdc&t=4293)]
Thanks.
