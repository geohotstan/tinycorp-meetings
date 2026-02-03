# 2025-12-29 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- emulator, RDNA3, speed up tests
- MLPerf LLaMA
- flash attention
- viz / fast gemm
- drivers
- ctype / image
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=7UqoXz6LfFE)

### Highlights

- **[Five Years of Tinygrad, Growing Need](#geohot-000016)**: Geohot reflects on Tinygrad’s evolution from a “toy project” into something increasingly necessary as mainstream DL stacks (e.g., Torch) accumulate more execution paths and complexity.
- **[Mission + Team](#geohot-000530)**: The company is ~6 people; the mission is to “commoditize the betaflop,” with an expectation it’ll take “five more years.”
- **[Renderer Unification Direction](#geohot-000554)**: Compilers are being moved into the renderer (done for CPU + AMD); the goal is for the renderer to take linearized UOps all the way to machine code, collapsing artificial “source vs assembly” distinctions.
- **[RDNA3 Tooling: Assembler, Emulator, DSL, Pseudocode Runner](#geohot-000554)**: Geohot describes a tightly unified RDNA3 environment (asm/mu/lib/pcode), including tests that compare short instruction runs directly against hardware and auto-extraction from vendor PDFs; CDNA4 is planned similarly.
- **[Make Tests Fast (Human-Scale Feedback)](#geohot-001025)**: Emphasis on tests that run in seconds; aim for ~30s on a modern 32-core machine, with willingness to delete or simplify stale/slow tests (while preserving coverage).
- **[RDNA3 Backend Progress](#geohot-001132)**: A separate RDNA3 backend effort is “pretty complete,” with ops tests passing except GEMM and one comm case due to register pressure.
- **[Hypothesis Rejection-Sampling Pitfall](#chenyu-001240)**: Chenyu identifies slow dtype tests caused by filtering/rejection sampling (e.g., generating values until they land in float8 range), and notes warnings were ignored; plans to fix.
- **[Test Suite Structure: Ops, Dtypes, ALU, Fuzzing](#geohot-001518)**: Geohot suggests organizing around “pluses” (test all ops, all dtypes, then fuzz combinations) and moving dtype-ALU coverage into dtype tests for clearer minimal test sets.
- **[Do It for Humans; Agents Benefit Too](#geohot-001701)**: The principle is not to optimize workflows for agents specifically—improving clarity and structure for humans also improves agent effectiveness.
- **[FlashAttention Blockers for LLaMA/BERT](#chenyu-001718)**: Chenyu reports dtype expectations and NaN issues (BERT and single-GPU LLaMA), plus multi-device mismatches; requests clearer asserts instead of silent casts that later NaN.
- **[Fast GEMM “fast GEMM” Integration Plan](#geohot-002243)**: A raw-assembly fast GEMM exists in master; discussion focuses on making it parameterizable and wiring it through Tensor flags similar to FlashAttention so LLaMA trainer can toggle it.
- **[Transpose/Pre-Transforms Are Cheap vs GEMM](#geohot-002404)**: Geohot argues transposes/contiguous pre-transforms are negligible compared to GEMM speedups, and Tinygrad should lean into such transformations when they unlock faster kernels.
- **[From Raw Assembly to DSL to UOps](#geohot-002658)**: Roadmap: move fast GEMM out of raw assembly into the assembly DSL, add macros, then (eventually) generate it from UOps.
- **[UOps→Fast Assembly Strategy: ThunderKittens-Like Layer](#geohot-002731)**: After trying greedy + ILP register allocators, Geohot proposes targeting a higher-level “ThunderKittens to raw assembly” approach and reshaping UOps to match that abstraction.
- **[IDA-Inspired Viz + SQTT Profiling Ideas](#geohot-002951)**: Desire for an IDE-like disassembly UI (jump between graph/flat views, highlight register uses, show raw bytes) and tighter integration with SQTT so hotspots/bottlenecks can be visually marked.
- **[Driver Status: AM on MI350 + XGMI Work](#nimlgen-003125)**: Nimlgen reports MI350 testing looks good with AM and LLaMA runs; added extra XGMI mappings (some speedup), but not yet using all faster P2P links; plans to improve all-reduce and parallelism.
- **[Selecting Interface via Env Var](#nimlgen-003317)**: There is an env var to force PCIe mode: `AMD_IFACE=PCI`.
- **[Driver Priorities + 2026 Goal](#geohot-003544)**: Priorities include optional SDMA (0. n queues) and improving training speed; longer-term goal by end of 2026 is “sovereign support” for both NVIDIA and AMD (not relying on external stacks), plus broader GPU environment tooling.
- **[Image=1 Performance: Pitch/Alignment Focus, Rip Out Old Paths](#chrism-003654)**: Chrism’s work targets making `IMAGE=1` fast; evidence suggests the slowdown is pitch/alignment-related (sampler configuration), not fusion; Geohot pushes to fix it generically and ultimately disable `IMAGE=2`.
- **[dtype.image Internal-Only + Rewrite Rules](#geohot-004210)**: Keeping `dtype.image` internally (for rewrite rules like simplify-valid) is acceptable, but it should not appear in the public tensor-facing API.
- **[Remove ctypes Struct/Union Abstraction](#chrism-004236)**: Chrism describes a PR removing `ctype structure` (and replacing unions/arrays/pointers support) to avoid hiding complexity; Geohot agrees surfacing that complexity is the priority.
- **[Renderers Shouldn’t Need Devices (OpenCL Exception)](#geohot-004654)**: Plan to remove “compiler pair/compiler set” in favor of a simple list of renderers; renderers should run without devices, with OpenCL treated as a special case due to its binary-dump limitations.
- **[FPA BERT Training Bounty](#geohot-005051)**: Geohot offers a **$2,000 bounty** for FPA BERT training once the work is merged and validated with a full training run.
- **[Multi-GPU Custom Kernel Fix + BEAM Search Instability](#geohot-005211)**: Geohot agrees to merge the multi custom-kernel fix; BEAM search sometimes fails to find fast kernels, possibly due to timing/timeout issues—raising timeouts may help.
- **[No “AI Slop” PRs](#geohot-005357)**: Strong warning: if using AI, contributors must scrutinize and clean the PR thoroughly; the value is correctness and cleanup, not dumping generated code (and don’t “fix” by skipping tests).
- **[Windows CUDA Testing Reality](#geohot-005635)**: CUDA-on-Windows CI isn’t a priority; Windows support should “fall out for free” from abstractions rather than become a maintenance burden.
- **[Wrap-Up + Release Mention](#chenyu-010053)**: Chenyu suggests making a release “this week,” and the meeting closes with “See you next year.”

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=0)]
Hello, everyone. This is the last meeting of 2025. And the star was company update. Five year celebration.

##### **Geohot** [[00:00:16](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=16)]
Yeah, I mean, it's been three years, a little less than three years of the company. Tiny grads first commit was a little over five years ago. The first two years, it was really a toy project. But I started to replace more and more of Qualcomm's SMP with Tinygrad. Like at one point, I just realized that a lot of the stuff I was writing for comma and a lot of the stuff I was writing for fun and Tinygrad were pretty much the same thing. And these basic building blocks of deep learning compilers are implemented over and over and over and over again. You know, and every every vendor has their own SMP. And so I think that's a really important thing to keep in mind. And I think that's a really important thing to keep in mind. And I think that's a really important thing to keep in mind. Because it's really hard to add back end compatibility to torch, nobody's going to add back end compatibility to torch for the Qualcomm GPU. And even if they did, it still isn't really what you want, because torch isn't a compiler. torch does not have a way to like export what's actually running on the GPU. And in a way, it kind of can't, because that's just not how it's structured. It's structured to be able to call torch does not have a way to like export what's actually running on the GPU. And in a way, it kind of can't, because that's just not how it's structured. It's structured to be able to call APIs at all different parts of the abstraction stack from C D and N to Triton to hand coded kernels in torch to falling back on CPU. So you realize that something else is kind of necessary. And it's interesting that in these five years, nothing else has really come along. torch compile is only focused on speed torch compile is not focused on being able to to export a minimum set of stuff. It's not really focused on being able to select the right display that chief shiny. And it's really kind of visible that the additionalSON literally just kind of you don't get to see. So yeah, I mean, I think five years in, TinyGrad is kind of more needed than ever because the stacks have only grown more complex. There has been no simplification in the deep learning stats. They have simply grown. It used to just be Torch had a bunch of CUDA kernels and CUDNN kernels, and calls to CUDNN. Now, well, Torch has five different paths. So it has CUDA kernels. It has CUDNN kernels because, of course, nothing ever goes away. It has Triton kernels. And it doesn't just have Triton kernels. Now it's starting to add Qt kernels, which is NVIDIA's custom DSL. And then, of course, it has the CPU fallback paths. There's actually five different ways in Torch to execute a thing that's supposed to just be CUDA kernel. But in TinyGrad, of course, there's only one way to do this. We compile it. We compile the CUDA kernel for the device. And even where we do have multiple paths, I want all of these to go away. I mean, it's not really multiple paths. The runtime is all unified. But we do have multiple compilers. Yeah. But once we unify all of this to the new way of doing things, I think that, yeah, the massive complexity in these stacks doesn't really need to exist. So it's going to take five more years. And then, of course, I hope everyone sees that when we do finally unify all of this stuff and get this down to something that can output GPU assembly languages, we then have all the pieces to output things to our own instruction set. And our own instruction set can be much simpler than instruction sets like I've been working with RDNA 3 all week, and RDNA 3 is insanely complicated. RDNA 3 has like a thousand instructions. And it supports all of this different stuff. And it's like, I've been working with RDNA 3 all week, and it's like, stuff and just like things that you don't need um you know i think that you could get away with uh probably a few more instructions than risk five because you're not it's not it's not risk you're not going to be doing any um microcode instruction coalescing super scalar stuff in your thing but a few basics and then you can have the instructions compound and they can compound in the same way that we always talk about which is not with the multiply but with the add right if you have a d type and an operation if you've fully abstracted your d type in your operation the complexity is additive not multiplicative but when you look at something like the RDNA

##### **Geohot** [[00:05:08](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=308)]
pre-instruction set the complexity is multiplicative so yeah five years of tinygrad that's the company

##### **Geohot** [[00:05:22](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=322)]
the deconstructionist company six people if you want to join us uh you know how to get hired here

##### **Geohot** [[00:05:30](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=330)]
and our mission is to commoditize the beta flop it's going to take five more years

##### **Chenyu** [[00:05:41](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=341)]
well

##### **Chenyu** [[00:05:44](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=344)]
great uh i also saw that you have been working on many stuff do you want to give a quick rundown for the things that you were trying um

##### **Geohot** [[00:05:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=354)]
sure um so the first thing i did was i added renderer i added compilers to the renderer uh i did this for cpu and for amd but um if anyone wants to take up the mantle of doing that for the other things i don't really like the compiler pair compiler set thing it should really just be a renderer the only tricky case is renderers that require the device and i believe that that is only open cl and i'm fine with just putting in a hack for open cl but everything that i've done so far has been a renderer and i've been working on a lot of things so i'm going to go ahead and do a little bit of a demo of what i've done with the renderer so the renderer should really be the thing that does the entire transformation from the uh uops down to the machine code there there is no arbitrary distinction except maybe for debugging between the source code and the assembly as we go to assembly backends i hope that's pretty obvious right so what the what the renderer does is takes a linearized list of uops and outputs assembly code that implements that linearized list of uops and then it's a little bit more complicated than the original one but even then we're probably going to want to add some back pressure uh to change the linearization order based on register allocation but i think that we can do that as a generic pass and it will still be i think that that instruction ordering pass will even benefit things like cbackends so uh yeah what i've been working on for the last week is a tightly unified uh so it's four files um it's it's it's uh asm uh mu lib and p code uh i'm gonna change it a little bit but asm is a assembler disassembler uh mu is an emulator lib is a dsl for uh writing the RDNA3 instructions in python and p code is a uh amd pseudocode dsl that allows us to run the pseudocode directly from the arden so if you look in the arden a3 pdf you'll see that every instruction has a bunch of pseudocode um it's 96 correct uh i have a great test now called uh test mu that can compare short instruction runs directly to the hardware so if claude is incredible at this i just say you know find discrepancies and i think now we're to the point where python remu has less bugs than remu uh but i I want to make Python Remu almost 100% perfect and match the hardware entirely. It's not going to be as fast as Remu, and we'll decide what to do about that. But, yeah, we have a full emulator. We have an assembler and disassembler, which can be used instead of LLVM. The really nice thing about our assembler and disassembler is when you disassemble from the LLVM string or from the machine code, from the machine code, you don't even need the asm file. You can just use the lib file. You can go from the bytes right to a Python class that is the instruction. So the Python class lets you extract from the bytes of the machine code what registers are being used, what op type it is, what specific op it is within that op type, so on and so forth. So I'm going to continue to work on that. It's not exactly how I usually code. Very clod heavy, but it's about 2,000 lines. And I think it'll.. Probably stay around 2,000 lines. And I probably have another week or two of work on it. But I'm just.. You know, it's so different. It's so different to code with these things. But it's been a lot of fun. And we have a lot of functionality already working. I think it's already being used in some of the Viz stuff. Yeah, but the idea should be it's an entire environment for RDNA 3. And, of course, it's not actually.. It's all extracted from the PDFs. So I have a clod working right now to extract all the stuff for CDNA 4 as well. So it's eventually going to.. It's going to be in assembly AMD slash RDNA 3, assembly AMD slash CDNA 4. But everything in the RDNA 3 and CDNA 4 directories is going to be automatically extracted from PDFs. And then it will function as an emulator, an assembler, and a DSL. I'm going to rename lib to DSL. I'll do that now. But, yeah. So that's what I've been working on. Probably have another week or two.

##### **Geohot** [[00:10:13](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=613)]
But then we'll have a full environment for using these things. Great. Any other complaints? One more.

##### **Geohot** [[00:10:25](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=625)]
One more thing. One thing that I found to be extremely helpful in writing this stuff and getting clod to be useful is having tests that run in 10 seconds. So, yeah. We need to really think about.. The OpenPilot people talked about this, too. You know, we have tons and tons of tests in TinyGrad. We should start thinking about what tests.. We can delete. What tests we can speed up. What tests we can make simpler. We want to get the test coverage, but we want it to run on a modern high-core count machine in, let's say, 30 seconds. You know, and it's okay if it takes five minutes in CI. But on, like, a 32-core machine, it should take, yeah, like 30 seconds to run these. So it's everything that's involved with this. NimbleGen, we have to fix the AMD OpenPilot. It opens lots of devices thing by falling back SDMA to normal copy, the same as the driver does.

##### **Chenyu** [[00:11:27](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=687)]
Yeah.

##### **Geohot** [[00:11:28](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=688)]
And I think that's basically it. But..

##### **Geohot** [[00:11:32](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=692)]
Oh, also, the.. I never would have been able to make this work without.. I also have another clod working right now on a RDNA 3 backend, which is pretty complete. I have all the ops tests passing except for GEMM. And one of the comms because of register pressure. But, yeah, it's using all the stuff. So, you know, things are happening now. But, yeah, speed-up tests. One of the things that I found so useful is having tests that run in seconds and not minutes. And I think that's useful for humans and machines and CI and everything alike. So if everybody here could work on speeding up tests, removing stale tests, and making sure PyTest without args passes on your machine, of course, you can use dash n. To run in parallel. But, yeah, if there's tests that are slow, that aren't really that necessary, think about what we need to cover. Feel free to delete. You know, if we're not putting 10% back, we're deleting too much. We're deleting too little.

##### **Geohot** [[00:12:29](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=749)]
So.. That's it about that.

##### **Qazalin** [[00:12:35](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=755)]
Cool.

##### **Chenyu** [[00:12:40](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=760)]
Before LLaMA.. So I also fixed a bunch of tests. So I think now everything runs locally. On my Mac. Fairly quickly. The only slow thing is in test D type. And it's specifically to how we use hypothesis. So hypothesis will generate some test data for you. And the way we use filter is wrong. For example, if you want to test something that has input to be float 8. Which has like maximum of like 400. Currently we use hypothesis to generate the filter until we see an example that's within the float 8 range. And of course, that would take forever. Because out of all the 32 range, float 8 is just a tiny portion of that.

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=814)]
We're doing like rejection sampling, I see.

##### **Chenyu** [[00:13:36](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=816)]
Yes. And to make it worse, someone, probably me or some other people just ignore all the warnings saying you are not a filter. You are filtering too much. It's actually filtering too much. It was complaining and we just not logging that. That was probably me.

##### **Geohot** [[00:13:55](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=835)]
I didn't like those warnings. Yeah.

##### **Chenyu** [[00:13:59](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=839)]
So this I will fix. And I think this is also the experience of how I use cloud to fix stuff.

##### **Qazalin** [[00:14:25](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=865)]
So basically, the way I use it is, I use my test to do all the tests.

##### **Geohot** [[00:14:26](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=866)]
And you hear me well. Yeah, you're back. You cut off.

##### **Chenyu** [[00:14:30](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=870)]
Okay. Yeah. So I agree with fixing the test fast. Also, I think we just need to be more mindful for like it's okay to have a lot of restrictions. regression test and test some bigger end-to-end stuff. But I think TestTiny is a good example for when we try things like this. If TestTiny pass, I have a very good confidence for it would pass everything. Then I think for CI, it's including the model and others. So having a good operation for slow stuff that can be skipped sometimes, I think is nice.

##### **Geohot** [[00:15:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=918)]
I mean, I don't think TestTiny is complete, but I do think that some of the large model integration tests are less necessary, depending on what you're touching. TestTiny is not going to test all the ops and is not going to test D-types. So what I found is if you run test ops, test D-types, and test ALU, test D-types ALU, those are pretty good. We should probably move test D-types ALU into test D-types. Because we should think about having basically a test suite. For each of the pluses that I was talking about before. You got to test all ops. Yeah, you got to test all D-types. And then you want to fuzz combinations of those. Yeah.

##### **Chenyu** [[00:15:57](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=957)]
Yeah, so I think this is the ideas when we think about how to remove stale tests. Because when TinyGraph was early, there might still be like a file code test conf or something like that. Like test a few confs or there was a test shape checker. That was removed because we removed shape checker. But things like that should be like how we integrate things into these pluses. If something specific about D-type, we move it to D-type test. If it's something specific about like scheduler, we find a correct place to put that. This will also help when cloud or your agent finds what test to be, it needs to run. So of course, naming it correctly is it. It's good for test discovery. But having these like functional separation for tests also helps. It also helps human, right? It's like when you make a change, you want to know what tests, the minimum tests you need to run before you try to CI the full thing.

##### **Geohot** [[00:17:01](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1021)]
Yeah, Harold has a good philosophy about agents is you should never do anything designed to benefit agents. You should do everything that benefits humans. It turns out it's the same stuff.

##### **Chenyu** [[00:17:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1038)]
LLaMA, I had very little update on LLaMA. I added more logging. So now you can run with, with SEM biases. Mostly I think it was where we talked more about flesh attention now. It's blocked on that. So I have two specific feedback for flesh attention. One is, I think now it only works or expected to work for certain D-type because there are a few tests here in BANA. and there, and if so, we need to make assert more clear instead of, I think of the current behavior now is it just do the cast, so if your D type is bad or not expected, it just like NAM somewhere. So I think adding some asserts there would help. For single, single GPU, it can run, but the output pretty much NAM instantly. I don't, I understand why. And for multi-device, there are some device mismatch. It might just, it might be the custom kernel thing with multi-GPU. So those two are my feedback on FlashAttention. Other than that, the training loop runs, maybe not the, not the fastest, but it runs

##### **Geohot** [[00:18:41](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1121)]
the compiles, but it runs the compiles. So, yeah, this is the NAN-ing is on BERT.

##### **Chenyu** [[00:18:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1134)]
NAN-ing is on BERT. And I think LLaMA single GPU as well. I see. Because, because BERT, BERT might be D type thing. I think you expect BFLOW 16. So maybe one of that is the different D type. I'm pretty sure the LLaMA one I tried was BFLOW 16. But that's why I want the assert to be there saying if it's not that D type, don't bother trying.

##### **Geohot** [[00:19:28](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1168)]
I will paste the repo somewhere so that you can, you can verify.

##### **Chenyu** [[00:19:39](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1179)]
So I expect FlashAttention, you would fix the thing.

##### **Geohot** [[00:19:43](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1183)]
Yeah. Just mention.

##### **Qazalin** [[00:19:46](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1186)]
Yeah. Cool.

##### **Geohot** [[00:19:49](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1189)]
You also add uh, Chris M to the all the tenant losses. Yes. Thanks.

##### **Geohot** [[00:20:00](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1200)]
Yeah, anyone who works here, you're welcome to grab my code code off, off of TR 9. And if that runs out of Blud Juice, I have two accounts now. Okay.

##### **Geohot** [[00:20:13](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1213)]
But yeah, that one should be pretty good if I want to use.

##### **Chenyu** [[00:20:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1218)]
I upgraded my $200.

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1223)]
Yeah, feel free to buy the $200 one with company cards or whatever.

##### **Chenyu** [[00:20:30](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1230)]
They also double the token allowance. Yeah, over Christmas. So everyone, this is a good time to try. Just try it. I just tried to let Cloud run directly on my machine because the web version was stuck installing Torch. And I got so annoyed. So I pretty much gave up my computer and said you can run whatever on this.

##### **Geohot** [[00:20:59](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1259)]
Yeah, yeah. They're not. I just trust it to. I don't even use Cloud code itself. I use OpenCode with Cloud. OpenCode has even less. There's also, OK, there's a flag for Cloud code to just allow permissions. So I just run OpenCode and pretty much allow everything and be like, I don't think it's going to send my SSH keys, post my SSH keys to the internet. So whatever. Who knows? That should be fine.

##### **Geohot** [[00:21:33](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1293)]
Yeah, feel free to run it.

##### **Chenyu** [[00:21:36](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1296)]
Yeah, probably company tiny boxes is fine too. Anyway.

##### **Geohot** [[00:21:40](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1300)]
Yeah, company tiny boxes. They're totally fine. I mean, at Comma, this is a bigger deal because we're worried about it doing things like deleting our data or copying our SSSQL tables or something. And that's more plausible, right? It's not going to go out of band and steal your Gmail cookies when it's working on this kind of thing, right? But if it is working in something, yeah. If it is, well, you shouldn't have CryptoWallet in your computer. But if it is, actually, I should move more stuff to a UVC. I mean, that's the real security model here to think about. But as long as it's not going to really step outside of what you're working on, it's not going to go that crazy. And there's not much damage that can be done to TinyGrad as an organization. Don't let it get pushed and stuff. Tell it not to. Yeah, yeah, yeah. Of course. Yeah.

##### **Chenyu** [[00:22:34](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1354)]
OK. Yeah, so hopefully we have a LLaMA training soon. Then we can really think about.

##### **Geohot** [[00:22:43](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1363)]
With that, we can move on to fast GEMM. There is in master a 1.3 page of platform. It's in raw assembly. It's for Torch users.

##### **Geohot** [[00:23:02](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1382)]
Is it parameterizable? Can we add an environment variable to use it?

##### **Geohot** [[00:23:14](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1394)]
Yes. Today I made it so that you can change the size. Yeah, cool. So I think you can maybe put it in Tensor.

##### **Qazalin** [[00:23:30](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1410)]
Sure. But it's an extra. Well, yeah.

##### **Geohot** [[00:23:35](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1415)]
I mean, I would put it in Tensor, the same thing that we did with Flash Attention. And then we'll just pass it in the same way. So you can send these use Flash Attention and use fast GEMM flags to the LLaMA trainer, and it should work.

##### **Geohot** [[00:23:52](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1432)]
Yeah, I tried it.

##### **Qazalin** [[00:23:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1434)]
It's also not a MathModeB. It's a MathModeB transpose. What?

##### **Geohot** [[00:24:04](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1444)]
Yeah, so what you can do is in Tensor, you can just transpose it however you want. Right? And you can add a contiguous. The time it takes to transpose a matrix is so negligible compared to the time it takes to do a jam. So I wouldn't worry about doing a pre-transformation on that. I think actually that's one of the mistakes TinyGrad is making, we'll eventually rectify, which is feel free to do these pre-transformations, because the speed of the pre-transformation is so fast, it's so negligible compared to the gains you get on the actual kernel. But yeah, it's great if we can just start using that. I mean, if we get Flash Attention and fast GEMM, I think we're most of the way to Fast LLaMA.

##### **Geohot** [[00:24:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1494)]
Also, test your custom stuff with Multi as well. I fixed your hardware test stuff. VOPD, so..

##### **Geohot** [[00:25:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1518)]
Oh, well, that one was skipped. I mean, by me, of course, I had Claude do it. I checked it, it was fine. But yeah, whatever you want for VOPD. I have a test in the future, and they're called Test Handwritten. And what I've been doing to fix bugs in the DSL is I'll just handwrite a bunch of tests that enforce the behavior that I want, and then tell Claude, hey, these tests don't pass. And it'll go and fix them.

##### **Qazalin** [[00:25:46](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1546)]
Yeah. My plan for Claude is also to let it fix my jam. There's a bunch of dead code branches in there that just, don't ever happen in the. I'm just going to let it use.

##### **Geohot** [[00:26:04](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1564)]
Yeah, that's great. The more you can get it to use stuff. I mean, yeah, we do have to watch out. I think everyone at this company is pretty good about this, but we do have to watch out for ever letting any slop in, because it can so quickly. I would say for every four times I run Claude, I only commit one. And I only commit that one after pretty aggressively telling it, clean up all dead code. Can you write this sentence? Can you write this with less lines? Can you write this with less lines while preserving functionality? Stop skipping things in the test. I know you want to skip things in the test. Don't do that. You know, I feel for the pressure that this model was cooked under. It must have been told many, many times that you really need to get it to pass. And sometimes it'll just decide to add a skip to the test to make it pass.

##### **Geohot** [[00:26:56](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1616)]
But, yeah, I think fast GEMM is great.

##### **Geohot** [[00:26:58](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1618)]
And then we can start thinking about how to move that fast GEMM out of raw assembly as much as possible. Like the first step can be moving it to our assembly DSL. And then the second step could be putting macros around our assembly DSL. And then the third step can be, you know, going from UOps to that assembly DSL, so on and so forth until we can emit fast jams.

##### **Geohot** [[00:27:22](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1642)]
Seem like a good strategy. UOps to fast assembly is very hard.

##### **Geohot** [[00:27:31](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1651)]
Well, so I've been playing with this quite a bit. I tried two register allocators. I tried a greedy register allocator and an ILP register allocator. I think that the way that we should think about it is not so much like that current thing is not really going to work. Like me just telling it right in RDNA3 render is not really going to work. I think that what we want to do is have something that looks more like Thunder Kittens to raw assembly.

##### **Geohot** [[00:28:01](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1681)]
I don't think that's that hard. And then we want to make our UOps look like Thunder Kittens.

##### **Geohot** [[00:28:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1698)]
Right. So a lot of the hard stuff about raw assembly is in this like micro scheduling stuff. Is in like decision making. Deciding, well, do I want to do all the loads and then all the adds? Or do I want to do some loads and some adds? Or do I want to interleave load add, load add, load add? I think Thunder Kittens largely answers this for us. And the answer is you want to interleave as much as possible, but not at the instruction granularity. Instead, at the Thunder Kittens register granularity.

##### **Geohot** [[00:28:52](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1732)]
So, yeah, I don't think this is that hard.

##### **Geohot** [[00:28:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1734)]
I think also we want to start moving away from using their.. We want to improve our SQTT parser. And we want to start using it. And, or I don't know, maybe that's not the highest priority.

##### **Geohot** [[00:29:11](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1751)]
But we want to start adding, like, did you try IDA at all? I didn't. Demo of IDA? A little bit.

##### **Qazalin** [[00:29:24](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1764)]
I did some things. I did download the demo. I tried, like, some very small C I wrote myself. But I didn't look in any, like, real binary. I mean, I see, like, you press space into it and it goes to the definition. It shows the graph and you click on stuff. But.. Yeah. I like the IDA UI.

##### **Geohot** [[00:29:51](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1791)]
I like the IDA UI. Where you can press space to go back to the.. To the flat disassembly view. You can click on a register. And it will light up all uses of that register. Which I think are pretty cool. And we should be able to do that pretty easily now with our AsmDSL. It will show you the actual raw bytes next to the instruction in the flat disassembly view. You know, I just think IDA does a great job with this UI. And the more that we can be like that, the better. And then we should also start, as we design the UI, be thinking about how to integrate the SQTT stuff with the assembly parse as much as possible. So, you know, for each one of those instructions, think about how to, like, light them up red if they're the bottleneck and stuff like that. You know, but yeah. Everything that you need to make a GEMM fast in an integrated development environment is good.

##### **Geohot** [[00:30:46](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1846)]
I think it's a nice loop. Cool. Thanks. Next, word drivers.

##### **Nimlgen** [[00:31:25](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1885)]
Yeah, so I've been testing MI350 and it looks fine with AM. So LAMA trains, Genio, you mentioned, also runs fine with AM. So I think we can switch our old machines. Yeah. And also test if you find something, I can look into this. So and also I added extra. GMI mappings. So it's already a bit faster, but I still don't utilize like all P2P links, which are way faster than. PCA in this case.

##### **Nimlgen** [[00:32:09](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1929)]
So, yeah. I think I'll experiment with all reduce to get the full performance because it's. Yeah.

##### **Nimlgen** [[00:32:25](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1945)]
So basically sending. Actually, we have some limitations in runtime right now because when we want to send chunks from one, like one to all, it will be serialized right now because we have only one queue is they make you. But potentially, XGMI can handle this in parallel at the maximum speed.

##### **Geohot** [[00:32:50](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1970)]
Yeah.

##### **Qazalin** [[00:32:51](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1971)]
Yeah.

##### **Geohot** [[00:32:53](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1973)]
So we don't have to do that.

##### **Chenyu** [[00:32:55](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1975)]
Speaking of using a and I don't remember, do we have a, do we have a flag that specify AM and because I had this issue that I thought I was running AM or I thought I was running with AMD and turns out it's not. And I only realize when I look into logs and stuff. Because it's not part of a device.

##### **Nimlgen** [[00:33:17](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=1997)]
Yeah. Yeah, we do have AMD underscore IFACE equals PCI to run again.

##### **Geohot** [[00:33:25](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2005)]
Oh, OK.

##### **Qazalin** [[00:33:29](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2009)]
Cool.

##### **Geohot** [[00:33:33](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2013)]
Yeah, so glad that's coming along.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2016)]
Yeah, I'm happy we can switch. You got the right idea with the all-reduced stuff. Yeah, this stuff's the highest priority. Yeah, you know, I'll say again how happy I am that we have our own driver. Because if you don't have a user-based driver, and you're letting Claude play with it, or even if you're playing with it yourself, there's just so many ways to crash their driver. So it's great to not have to worry about that. I haven't had to reboot TR9 at all using AM. I'm sure if we were using AMD, I would have had to reboot it 30 times. So yeah, that's great. Yeah, so two other things with the drivers. I think SDMA should be optional. I think maybe this is part of the total SDMA refactoring, where you can have, right now it's one queue or two queues. You can have n queues, and n can also be 0. So if there's no SDMA queues, it will just use kernels. If there is multiple SDMA queues, it will use them as appropriate. Yeah. And then just in the back of your mind, the HVAC decode speed. Any progress on that?

##### **Geohot** [[00:34:50](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2090)]
No.

##### **Nimlgen** [[00:34:53](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2093)]
Actually, I thought you said something about JIT refactor. I don't know if this would help anyhow. About which? I mean, you spoke something about JIT refactor.

##### **Geohot** [[00:35:07](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2107)]
Oh, the JIT refactor. Yeah. If you think about it, it's a little bit more complicated. I do think that it's mostly just, if you think that the code is mostly good, and it's just JIT refactor, you can leave that for me. I'll get back to the JIT refactor at some point. That's, yeah. If you think it's really just the JIT, then I think we can leave that where it is, and just focus on the AMD stuff. And then also, yeah, if you have a side project you want to work on, add the HVAC parser to AMD as well. I'm sure they have one.

##### **Nimlgen** [[00:35:43](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2143)]
Yeah. Yeah, OK.

##### **Geohot** [[00:35:44](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2144)]
It'd be nice to have that effect with both of them. I mean, to kind of set where I want to be at the end of the year, the end of 2026, I want to have full sovereign support for both NVIDIA and AMD. Not even using NAC, not using anything. Just like the same way that we can schedule RDNA3 instructions, CDNA4 instructions, we should be able to schedule SASS instructions too. So I really make sure we fully understand these things by the end of the year. Yeah, and then extractions to use things like the video decoder,

##### **Geohot** [[00:36:19](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2179)]
really just a full environment for the GPU.

##### **Qazalin** [[00:36:23](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2183)]
Cool.

##### **Geohot** [[00:36:25](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2185)]
Yeah, main thing should just be increasing LAMA training speed on our driver. Mm-hmm. So yeah, Chen is having trouble with his internet.

##### **Geohot** [[00:36:51](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2211)]
Yeah, let's move on to C-type image.

##### **Chrism** [[00:36:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2214)]
Cool. Yeah, so yeah, I guess I'll start with the image equals one stuff, or making image equals one fast. I have a PR open for that. I didn't really work on it last week, but you know. Yeah. Yeah. So that seems like it's probably in pretty good shape. Basically, the sort of realigned it a little bit more to just be focusing on making image equals one fast, and then not really messing with what image equals two is doing. So basically, the way I was going to do that was going to say, you can sort of optionally specify that a buffer needs to be cast to being an image buffer, or whatever this means. So you can still have your old image D-type buffers. Nope. And those have all the custom allocated, the alignment padding.

##### **Geohot** [[00:37:42](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2262)]
Yeah, I mean, I wouldn't spend time on it. If it's anything more than a simple if statement, I wouldn't spend time on it, right? The future is image equals one, and the rest of the stuff has to be ripped out. Now, it can't be ripped out until we don't regret OpenPilot. But there's no point in putting a fallback in if it's just so I could get, just so you can get something merged, right? Let's figure out why is image equals one still slower than image equals two. Is it only alignment?

##### **Chrism** [[00:38:09](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2289)]
Yeah. My understanding is it's only alignment. It's only specifically the pitch add. When I commented that out, the image equals one is the same speed as the image equals two.

##### **Geohot** [[00:38:21](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2301)]
Got it. So we need to come up with some generic way to fix this. I think there's no point in wasting any time on fallback stuff, right? We're going to rip all the image D-type stuff out. We just need to find some way to fix this. So you're saying if you add pad, the kernels don't fuse like how they used to fuse.

##### **Chrism** [[00:38:38](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2318)]
No. All right. All right. They don't fuse like they used to fuse. That's like there's literally two kernels that do that. I need to look at specifically what those are doing. But that's not actually the slow part. The slow part is the accesses, I'm pretty sure. Like the fact that the data is not in the same format. Like I don't know exactly if it's a cache hit rate problem or what it is specifically. But it doesn't have to do with the fusing. You can look at the kernels that are running. It's the same code. It's like literally the same assembly. But it's just slower because of the way that the data is laid out, like the way that the sampler is running.

##### **Geohot** [[00:39:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2358)]
Got it. But OK. So but it is a change to the code, right? Like you're changing the pitch, not just the overall alignment to the buffer.

##### **Chrism** [[00:39:27](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2367)]
Yes. But the sampler handles all of that. So it's just a sampler configuration. So the assembly that gets outputted is the same.

##### **Geohot** [[00:39:34](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2374)]
Yeah, I totally understand. Yeah. So I mean, what you need to do then, is, you know, is make the, oh, I see what you're saying. The sampler is actually doing that multiply for you. So it's not even the same. But it's different code.

##### **Chrism** [[00:39:45](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2385)]
Exactly. Yeah. Yeah. Yeah.

##### **Geohot** [[00:39:47](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2387)]
Yeah. Yeah. So I mean, yeah, what you need to do is find out a way to get. So again, you can change those methods, that image conv method and that image GEMM method, all you want. If you want to manually specify pads, shrinks, all of those things, that's totally fine. But yeah, I mean, I think that what you think needs a special annotation. To say, like, this is padding. I don't think you actually need that. I would suspect that if you try to do it, and it outputs something different in the assembly, you could probably find some rewrite rules that will clean all of that up. And that's kind of the whole philosophy of TinyGrad. The philosophy of TinyGrad is like, OK, yeah, I can specify pads here. And then these pads, of course, don't actually have to like, we don't actually have to write zeros to any buffer or anything. So yeah.

##### **Chrism** [[00:40:36](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2436)]
No, that makes sense. That makes sense. That makes sense. I think you're right that that can all be expressed in a rewrite rule. Yeah, I just have to think about, I did try and fiddle with the image conv method. And I incorporated some of the logic there. And so there were some speedups we had. But the specific thing is like, in some cases, you add this additional value to the pitch. So you always round the pitch up to a certain value. But you additionally add more padding in certain cases. And that was the thing that was difficult for me to encode. But I think I can probably figure out a way to do that.

##### **Geohot** [[00:41:14](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2474)]
Got it. Yeah. But yeah, I'm totally fine with you messing with those methods all you want. I mean, you're going to have to change those methods anyway to not use dtype.image. And I wouldn't worry about any intermediate thing. I would just rip it out all at once, get image equals one to be fast, and then disable image equals two.

##### **Chrism** [[00:41:29](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2489)]
Yeah. And the one thing I was thinking about with respect to removing image dtype or dtype.image is that you still kind of want a way to track this within your code. And when you're doing all the rewrites, like the simplify valid stuff, you still need to know that this is an image dtype to know that you can do the simplify valid. So doesn't it make sense to keep tracking it using that? Or should we be tracking that information some other way?

##### **Geohot** [[00:41:58](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2518)]
Yeah, so I wouldn't be tracking that with, oh, oh, you're saying you want to keep dtype.image as the place so that the rewrite rules understand that things are an image?

##### **Chrism** [[00:42:09](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2529)]
Exactly, yeah.

##### **Geohot** [[00:42:10](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2530)]
Yeah, and then you want to have a rewrite rule that changes it to dtype.image? Yeah, I'm fine with that for now. I mean, maybe we'll change it to something else later.

##### **Chrism** [[00:42:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2538)]
Yeah.

##### **Geohot** [[00:42:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2538)]
Yeah, no, I'm not that worried about how it does it internally. The main thing that I'm worried about is that there should be no dtype.image in the tensor stuff.

##### **Chrism** [[00:42:28](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2548)]
Yeah, that makes sense. Yeah, it's similar to dtype.index, right? That's not exposed to the user.

##### **Geohot** [[00:42:34](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2554)]
Yeah, yeah, that's actually fine.

##### **Chrism** [[00:42:36](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2556)]
OK. OK, and then the ctype stuff, I also have a PR open that's removing ctype structure entirely. You also have to replace unions, obviously. But arrays and pointers also need to be replaced because you need to be able to support having arrays of structs and also having pointers to structs. So I think the way I got that implemented was not too bad. Like, in very rare cases, you have to do the slow path where, where if you pass by value, like a pass a struct by value or pass a union by value, then you have to cast it to a C-type thing so that the C-types can understand what you're looking at. And so that's probably a slower path, although it shouldn't be that slow. And then, oh yeah, also if it returns a struct, you need to cast that thing. So I just haven't gone through and made sure. I think there's some stuff that we probably need to change to make sure everything's compatible. So I just want to make sure I run all those tests before I can merge that. But that looks like it's probably in a pretty good state. Yeah, it might be nice eventually to replace everything that C-types does, or at least all the type stuff that C-types does. So that would mean, oh, maybe we, rather than doing C underscore bool and C underscore int and this sort of stuff. You could.. You could have your own versions of these things. And in particular, you could just.. Like, maybe we could unify this all with the stuff in D-types.py. But yeah, that's where that's at.

##### **Geohot** [[00:44:14](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2654)]
I think that's less important. Yeah, I mean, I think the important thing is just to deal with.. One of like, you know, when you think about Elon's process, I put something in front of the whole process, which is you need to surface all complexity. And it's unfortunate that what C-type structure is doing is actually hiding a lot of complexity. It's hiding a lot of opinion and complexity. So that's why it's really important that we switch that. Whereas like C-types bool and stuff, I don't know. That doesn't seem like.. Unless there's some complexity there that I don't understand. Yeah.

##### **Chrism** [[00:44:43](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2683)]
The only reason that you might want to remove this stuff is just because like now we kind of have two.. Like, basically, I need to parse this stuff. So for instance, you say of a struct that has like an int and a bool and whatever in it, then, you know, I have to be able to understand those things. And so I'm already writing a bit of code to be like, okay, like, you know, like, pack this into a bool or pack this into an int when you actually want to assign the things. I don't remember exactly. It's been a while since I looked at this code. But if I remember correctly, I had some feeling that I was like, oh, like, this would be maybe a nice thing to do. But you're right. I think it's probably better dictated by, you know, is this causing a frustrating problem? Or like, is there some issue that comes up because we didn't do this rather than saying, oh, let's do it proactively?

##### **Geohot** [[00:45:28](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2728)]
Yeah. I don't think we have to do any of that. But yeah, no, I'm happy to hear. Yeah. The C type structure thing is going to be good. The image thing is going to be good. Yeah. Hopefully those can be done this week. And then, yeah, we can think about, yeah, sort of what your next project is going to be.

##### **Chrism** [[00:45:49](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2749)]
Yeah. Yeah. And the one other thing, which you mentioned a little bit earlier, was the new style compilers. And I was going to try it. That's something I just worked on this morning. I have a third peer. Yep. I saw that. Okay, great. And I think maybe I didn't look at LVP yet, or LV and pipe, but that should be presumably also simple. You were complaining about there's something in op CPU. That's not great.

##### **Geohot** [[00:46:15](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2775)]
Oh, yeah. In op CPU, you're linking to the math library when you use LVP. I don't know if there's a way not to do that. You have a check in CPU program. Like CPU program should be agnostic of what renderer was used to create the program.

##### **Chrism** [[00:46:30](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2790)]
Yeah.

##### **Geohot** [[00:46:33](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2793)]
So I think that's something that's going to be a little bit more complicated. I don't know. That makes sense. I don't know. Yeah. I mean, all of the on pipes kind of, it's just annoying. Like, it's nice that we have NIR for Qualcomm and for NVIDIA, but I don't know. It's not a big deal. But yeah, no, if you want to actually, if you want to take that project entirely and move all the compilers, since you're kind of working in that area.

##### **Chrism** [[00:46:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2814)]
Yeah. Yeah, I definitely could do that. Like the other thing that we were discussing was like, okay, like, want to be able to do the null backend thing for, for the NVIDIA. For, you know, everything that we can. And so that's like a sort of related thing, I think that that would be worth doing.

##### **Geohot** [[00:47:08](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2828)]
Yeah. Yeah. I mean, I think that'll basically, I want to remove the compiler pair compiler set stuff, and then it's just simply a list of renderers. And then the renderers can run anywhere. Again, something special has to be done for stupid open CL. I can't believe their library. I can't believe their API is so bad, but. Yeah. Yeah. No, I mean, all those facts are metal, but yeah, I think, I think this is a, this is a good project kind of a, in your wheelhouse. Okay. Yeah. To get all the compilers moved to, but yeah, hopefully, hopefully you understand like, like the reason for the change. It's kind of like there, there really is no distinction between a renderer and a compiler. Like, sure. You want to keep this source thing exposed for like Viz and debug equals four. Yeah. But other than that, it's just a renderer takes the U ops and turns them into machine code.

##### **Chrism** [[00:47:53](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2873)]
No, I mean, I think NUR is the most obvious example of this because like we're outputting basics D four from the renderer. So it's like, this is total crap.

##### **Qazalin** [[00:48:00](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2880)]
Yeah. Yeah. Yeah.

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2881)]
Yeah. Yeah. Yeah. Yeah. But whenever we're out putting the Python back, it is outputting day 64 too. So yeah, those would be great to just entirely remove. And then we can put some flag to like this or something that says, sorry, this one doesn't have a, this one doesn't have an intermediate or it's really just. Yeah.

##### **Chrism** [[00:48:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2898)]
I mean, the thing is the NUR does have a visualization, but you have to run, you know, you have to dump it using the special thing that the, like within the, within Mesa.

##### **Geohot** [[00:48:28](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2908)]
Yeah. I mean, we might even want to expose that. Right. Like I, it could almost be, it could be render dependent how we dump this intermediate view, whatever we call it.

##### **Geohot** [[00:48:40](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2920)]
Yeah. That makes sense. Yeah.

##### **Geohot** [[00:48:41](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2921)]
I want to like, yeah. Remove the distinction more between renderers and compilers, but you know, again, still make it accessible, like, you know, the API accessible from the outside so that you can just compile something pretty easily. But the key thing is that renderers should never, ever need to be built. Need devices. Renderers should not use devices at all. And I kind of think what the answer for the open CL thing is going to be is that we're just going to start passing the string into open CL and we're going to put the compiler in CL program and just take that performance. It's not like open CL performance really matters that much.

##### **Chrism** [[00:49:19](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2959)]
Okay. I'll have to look at the open CL pipeline a little bit more to understand exactly what you mean, but it sounds good.

##### **Geohot** [[00:49:24](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2964)]
Yeah. Yeah. Well, I'll explain it quickly. It's it's basically an open CL. There is no way to get the. Bunch. Binary without opening the device. So an open CL, the way that it works is that you open the device, you create the kernel for the device, and then there's a special method which can dump out binary for the device. But I think that the solution here might just be to the only reason I want to bring this up is because it's an opinionated decision. And I think that the opinion is just sorry, open CL has a has a crappy API and now it gets crappy speed because of it.

##### **Chrism** [[00:49:57](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2997)]
Yeah. Yeah. Okay.

##### **Geohot** [[00:49:59](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=2999)]
Yeah. And we probably still want to keep some cash like we can keep the cash in CL program, but it will just be CL program that has a source and stuff.

##### **Geohot** [[00:50:08](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3008)]
And that's just CL that's dealt with like this. Yeah. Cool. Okay. Yeah. No, I, I like that a little bit. Stupid open CL. Um, yeah, I mean, I wish it had some way to run the compilers, but great.

##### **Geohot** [[00:50:25](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3025)]
Uh, cool. Uh, so I don't know that much about FPA BERT, but, uh, yeah. B1 TG, you tell me if I, if I owe you a bounty or not.

##### **B1tg** [[00:50:37](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3037)]
I'm not sure if it's a bounty. Have a draft PR open now. And, uh, we'll do, uh, do some full train run on this branch to make sure everything works.

##### **Geohot** [[00:50:51](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3051)]
I'm definitely happy to pay out a good size bounty for that once we get it merged. Um, yeah, if we really have FPA BERT. Training working, I'll put a $2,000 bounty on that. Uh, I'll put a $2,000 bounty up lock to you. Uh, FPA BERT training $2,000. Uh, yeah, but that's once that's once it's all merged. Sound good. Cool. Uh, but yeah, so, uh, I don't know what, if there's any blockers on our side, uh, for you to merge that.

##### **B1tg** [[00:51:27](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3087)]
I have, uh, my team. I have a multi GPU bug fix, uh, last week.

##### **Geohot** [[00:51:34](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3094)]
Uh, you have a bug. Oh, you, you want me to merge a fixed. Uh, is it, is there a PR number?

##### **B1tg** [[00:51:44](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3104)]
Yeah, you have, you have few comments on this.

##### **Geohot** [[00:51:53](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3113)]
Uh, oh, I commented on this.

##### **Geohot** [[00:51:56](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3116)]
Okay. Let me see.

##### **Qazalin** [[00:51:58](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3118)]
Okay.

##### **Geohot** [[00:52:02](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3122)]
Uh, which PR number?

##### **Chrism** [[00:52:06](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3126)]
Oh, yeah.

##### **Geohot** [[00:52:11](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3131)]
Multi custom kernels for input mixed with copy and shark. Um, yeah. Yeah.

##### **Qazalin** [[00:52:20](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3140)]
Yeah.

##### **Geohot** [[00:52:22](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3142)]
I'll merge it. I'm fine with that. I still think that, like, I'm not sure why you're not doing shard. Axis equals none. Uh, but I don't know. This is fine. I'll just merge it. This block. Yeah. This isn't that well thought out. Oh, arch. Anything else?

##### **B1tg** [[00:52:52](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3172)]
And seems BEAM search, um, is not very reliable. Sometimes he can't find. And the faster kernel. So I have to do the research. It's a take a one hour.

##### **Geohot** [[00:53:12](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3192)]
You know why it's not finding fast kernels. I mean, so I know that we have some timing issues with some of the Nvidia GPU current, or some of the AMD GPU kernels. And I don't know if that's what it's hitting. Uh, but yeah, definitely if we're, if we're hitting, like if there's timing issues, then the BEAM is going to be unreliable. Um, but yeah, if it just doesn't work overall, I don't really know what to say.

##### **Qazalin** [[00:53:35](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3215)]
Okay.

##### **B1tg** [[00:53:38](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3218)]
So I just raised the timeouts. Maybe I will find the timeout kernel to post it.

##### **Geohot** [[00:53:50](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3230)]
Sounds good. Cool.

##### **Geohot** [[00:53:57](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3237)]
Uh, yeah. So. So for other bounties, um, I'll talk about kind of the problem that I've been seeing in general with, uh, pull requests from new people. So, uh, you know, again, I'll give the general warning. Um, if you are going to use AI, you better scrutinize the shit out of that pull request, uh, before you show it to me, right? I'm not going to read your AI slot. If I wanted AI slop, I have access to better AI's than you, uh, or the same AI. If you're using Opus 4.5, I have access to the same AI as you. Um, and you know, I, I think that I'm better at prompting than the average person who's submitting. So if you're submitting a pull request generated by AI, you're wasting everybody's time, right? Like don't do that. Um, the value that you can add by submitting a pull request is making sure that you've 100% scrutinized that pull request. Uh, so it's just going to get harder in general as AI. Can kind of one shot these bounties, right? Like it's almost to the point now where if I spun up 10 instances of Claude and told all the Claude's to solve the bounties, it would solve probably one of them. If I gave it 10 bounties, it would probably solve one of them. The problem is now the value add is no longer in writing the code. The value add is figuring out which of the 10 it actually solved correctly in a reasonable way, getting it merged and getting it cleaned up. Um, so that's it. That's like, unfortunately much harder, uh, for us as a company to do. Like it's going to make the, the, the hiring process here even more sort of like open-ended. Like you have to give me pull requests that just show me that they clearly add value. Um, and you know, something that doesn't take me a long time to figure out if the pull request clearly add value. Um, you know, this is just the, the, the, the, yeah, the AI problem in general. Um, all right. You want me to merge your, you want me to merge your, your, uh, your, uh, your, your, uh, you got to whisper PR for me to merge. Uh, the CUDA binding on windows. I see your CUDA binding on windows PR and I'm kind of like, I don't know about this. Um, that seems fine, I guess. Get config vars to change the auto gen, all the tests pass. It's a gap that just does nothing there. Okay. That seems okay to me.

##### **Chrism** [[00:56:29](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3389)]
Is it possible for us to like actually test CUDA on windows like in CI or is that not?

##### **Geohot** [[00:56:35](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3395)]
Well, I don't really know how we would, I don't know if we care about it that much. Um, like that, that, that PR is clear that it's not gonna, it's not gonna break anything. Um, yeah. So I don't know. I don't, I don't think we care about it. I look, we could set up a computer and then have to test it the same way we test. Uh, the other thing is in our benchmark. But I do not want to, it's bad enough that we have to manage max in our benchmark. I definitely don't want to start to manage windows. Um, so yeah, I think it just kind of is what it is. Oh, you're trying to test it in CI. I mean, if you can figure out some way to do it, if you can figure out how to somehow test it in actions, that'd be great. But, uh, yeah, no, I don't think we should put time into that. I don't really care that much about windows. I care enough to have those basic windows test runners, but, uh, you know, tinygrad had windows support. Then windows support was removed when I realized I could delete lines. Then it was added back in when I realized that it wasn't actually any more lines anymore because we'd abstracted everything. So we kind of want like windows support to just fall out, uh, for free or it's not worth

##### **Geohot** [[00:57:36](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3456)]
it. So, okay, cool.

##### **Geohot** [[00:57:41](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3461)]
Um, yeah, I, you know, I, it's been, it's been harder to like update the bounty sheet in this new world of AI. Um, kind of because also like we're almost entering a world where if you can specify how to do something. Like that's the whole thing.

##### **Geohot** [[00:58:14](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3494)]
Um, and you put on like 12, it's, you know, like a web or whatever code content, like Like you can Google do that in like client pages. This code is kind of.. I see a lot of use of after, and I don't think it should have to use after that much. I'm fine with that regression. Yeah I wonder if there's some..

##### **Geohot** [[00:58:47](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3527)]
So like why are there two paths there? Like in that de-vectorizer, can both paths.. I mean it's just using after too, I wonder if both paths can use the same thing. I think that this can be cleaned up, but I definitely like the idea.

##### **Geohot** [[00:59:12](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3552)]
Yeah, I just wonder if that code can be cleaned up, but I like the PR. I don't know if that counts for any of the bounties. But that's definitely worth something. If it can be cleaned. Cool. Yeah. I think that's basically it. Let me see. Let me just look at this Whisper PR quickly. Like remove all the SFTT stuff.

##### **Chenyu** [[00:59:52](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3592)]
Okay.

##### **Geohot** [[00:59:54](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3594)]
Where is this? So I'm looking at this. I don't see it removing any.. It should remove some..

##### **Geohot** [[01:00:12](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3612)]
It should remove some.. Oh I guess we still need Librosa for the test.

##### **Geohot** [[01:00:18](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3618)]
Yeah I don't know how to deal with this right now. But yeah. Yeah, I mean I don't wanna support.. Oh, you finished first. No, that's all I got.

##### **Geohot** [[01:00:41](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3641)]
I don't want to support both. I don't want to.. I definitely don't want an environment variable that has new and old SFTT blah, blah, blah.

##### **Geohot** [[01:00:50](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3650)]
Okay. Oh, so let's close some of the steps.

##### **Chenyu** [[01:00:53](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3653)]
And let's make a release this week.

##### **Geohot** [[01:00:57](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3657)]
Maybe in a year or whatever.

##### **Chenyu** [[01:00:59](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3659)]
Sounds good. Cool.

##### **Geohot** [[01:01:02](https://www.youtube.com/watch?v=7UqoXz6LfFE&t=3662)]
Thank you, everyone. See you next year. Bye.
