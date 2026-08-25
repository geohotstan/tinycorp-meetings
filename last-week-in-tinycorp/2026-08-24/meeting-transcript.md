# 2026-08-24 Meeting

### Meeting Agenda

**Time:** new meeting #34, 8/24 9am Monday San Diego time
- company update
- CI infra
- PARALLEL, Qwen, rangeify
- CONST weak dtype
- HCQ2
- GPT-OSS
- fast LLaMA training
- release, bounties, RDNA3, comma happiness, Kimi


### Audio

[Youtube Link](https://www.youtube.com/watch?v=2CIBfxmsyLI)

### Highlights

- **[Company Update](#geohot-000000)**: AMD MI350Ps received; $100,000 wired to AMD for the secret project; 72 RTX 5090s at ~$5,000 each approved for Exa Box buildout; three 4090 CI machines listed for sale at $38,000.

- **[CI Infrastructure](#chrism-000254)**: Docker image for CI ready, eliminating the `setup tinygrad` step; multi-GPU NVIDIA jobs factored out ahead of machine sales; compile server built for QCOMCL via Docker/QEMU.

- **[CI Performance Target](#geohot-000508)**: No tinygrad CI job should exceed three minutes; expanding from 2 multi-GPU NVIDIA runners to 8 single-GPU runners for better parallelism.

- **[Parallel Compilation](#geohot-001141)**: Compilation infrastructure now shared with BEAM—UOps pickled across process boundaries for child-process compilation; considering future `enter_calls=subprocess` option for CALL lowering.

- **[Qwen Kernels Merged](#geohot-001325)**: Three kernels (GGML quantized linear, Flash Attention, Delta attention) merged; more than doubles speed compared to BEAMed results.

- **[CONST Weak Dtype](#chenyu-001714)**: All renderer changes merged; ~95% of dtypes no longer need to be UOp attributes; final flip planned after release.

- **[HCQ2 Performance](#nimlgen-002107)**: Enqueue time sometimes better than HCQ1; 288-copy overhead identified because Python isn't an HCQ2 device, creating synchronization points between devices.

- **[Memory/Compute Device Separation](#geohot-002249)**: Long-term vision to separate compute devices from memory devices—Python and CPU should share the same allocator; eventual goal is no "HCQ device" concept, just devices with memory and compute engines.

- **[GPT-OSS Training](#wozeparrot-003326)**: Now at ~900ms/step (3h13min), down from 1.2s; GEMMs at ~1 PFLOP FP8; ~300ms compute reduction still needed to hit target.

- **[LLaMA Training](#qazalin-003908)**: 1h57m achieved after fixing RoPE frequency BF16 precision bug; target shifted from AMD's time to NVIDIA's ~1h22m benchmark.

- **[Register Allocator Strategy](#geohot-005005)**: Plan to strip registers from handwritten assembly and apply tinygrad's register allocator, then work backward—removing instruction selection to reach a dialect where LLMs excel.

- **[Release v0.14](#geohot-005713)**: HCQ2 ships off by default behind a flag; release tagged same day as meeting.

- **[RDNA3 Backend](#raine-005850)**: Ready for review—VGPR/SGPR spilling added, regalloc logic fixed, one remaining `tan` regression from subregister spilling.


### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=0)]
Yeah, good progress. I talked with AMD. I don't know whether we got the MI350Ps last week, but we got them this week. I also sent them money for the secret project, so they took our money. That's good.

##### **Chenyu** [[00:00:14](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=14)]
Oh, it's getting real.

##### **Geohot** [[00:00:16](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=16)]
Yeah, it's getting real. I wired $100,000. We'll see what we get.

##### **Chenyu** [[00:00:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=26)]
Is that my script?

##### **Geohot** [[00:00:28](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=28)]
Yeah, that's the main thing. We also sold another tinybox Pro V2 Blackwell. We have a lot of those cases left, so it's good that we're selling them. We're buying 5090s for the new Exa Box too, and they're insanely overpriced at about $5,000 each.

##### **Chenyu** [[00:00:54](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=54)]
How many are we buying?

##### **Geohot** [[00:00:57](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=57)]
Seventy-two.

##### **Chenyu** [[00:00:59](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=59)]
Oh, God.

##### **Geohot** [[00:01:01](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=61)]
What else are we going to put in the Exa Box? We're getting more support from comma resources on the secret project, so Igor can focus on the Exa Box. I approved the spend for the 72 5090s and everything required for the initial Exa Box buildout.

##### **Chenyu** [[00:01:27](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=87)]
Sounds good.

##### **Geohot** [[00:01:33](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=93)]
I think that's it. Oh, we're also selling three 4090 machines. They were $35,000, but now they're $38,000 because some guy said he could build them himself. Good luck, guy.

##### **Geohot** [[00:01:54](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=114)]
There are a lot of foot guns when building these machines. If you do it slightly wrong, you get problems. The motherboard he chose has slot-to-slot signal-integrity issues. I don't think you can get full signal integrity to all the PCIe slots with that layout. Old-school PCI was a bus, so putting slots in a row made sense. PCIe is not a bus; it's a point-to-point fabric. If you want to buy our computers, they're nice computers. They were used in our CI for a while, and we have two for sale.

##### **Chenyu** [[00:02:47](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=167)]
Sounds good. We can move on. Let's start with CI infra.

##### **Chrism** [[00:02:54](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=174)]
Closely related to those machines going away, we can't run CI tasks on them anymore. I've been preparing for that. We won't have NVIDIA jobs that rely on multiple GPUs, including a LLaMA 3 four-GPU test and some ResNet jobs. I factored those into a multi-GPU job, so we should be able to disable that job for the NVIDIA GPUs.

##### **Chrism** [[00:03:36](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=216)]
I've also been cleaning up CI. We now have a Docker image that can run CI. I still need to test it in Gitea, but I tried several backends locally and it seems to work. That means the entire `setup tinygrad` step can essentially be skipped. It will just check that nothing is missing, and it should be fast.

##### **Chenyu** [[00:04:13](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=253)]
Will that prepare us for multi-machine CI?

##### **Chrism** [[00:04:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=260)]
I haven't thought about that yet. Do you mean running one job on two machines to test remote execution?

##### **Chenyu** [[00:04:32](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=272)]
Yeah. It isn't a hard blocker, but after HCQ2 is done, we want some form of multi-machine testing in CI. As long as this doesn't actively block that or make it impossible, it's fine.

##### **Chrism** [[00:04:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=288)]
I'll have to think about how that should work. It may become more obvious once we set up the Gitea CI runners and can see exactly how they work.

##### **Geohot** [[00:05:08](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=308)]
The new CPU-heavy CI machines will each have two 3080s and two 7600s. We're going to normalize running many small things on GPUs.

##### **Chrism** [[00:05:24](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=324)]
Since it will all be containerized, we need to work out whether the network card goes into the container, whether two jobs start simultaneously, or whether one job connects to another machine.

##### **Geohot** [[00:05:49](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=349)]
There should be one controller and a group of machines waiting to accept remote jobs. Remote fabric could use the same model. This could also decouple PCIe from everything else: the computer with the GPUs wouldn't have to be the controller.

##### **Chrism** [[00:06:19](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=379)]
That's true. Then every test would exercise remote execution.

##### **Geohot** [[00:06:35](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=395)]
That works if remote execution doesn't add too much overhead.

##### **Chrism** [[00:06:44](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=404)]
The other thing I built is the compile server. It lets you compile QCOMCL on any computer, using either Docker or QEMU. It isn't parallel. CUDA support is also a little better on Mac now. There's a related bounty, but MOCK requiring CUDA 11 is annoying because I put CUDA 12 in that container.

##### **Chrism** [[00:07:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=446)]
Someone opened GPU Ocelot PRs to fix that. If they're listening: you need to test the changes in tinygrad. I need to see tinygrad's tests pass, not only GPU Ocelot's tests.

##### **Geohot** [[00:07:44](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=464)]
I don't trust GPU Ocelot's tests very much.

##### **Chrism** [[00:07:49](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=469)]
Certainly not its SM50 tests. It probably didn't have tests for SM50.

##### **Geohot** [[00:07:55](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=475)]
Especially if you used AI to do this, don't stop there.

##### **Chrism** [[00:08:02](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=482)]
That's everything I have.

##### **Geohot** [[00:08:07](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=487)]
When will everything be down to three minutes? I don't want benchmark tests that take forever.

##### **Chrism** [[00:08:14](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=494)]
I'll factor the benchmarks into smaller pieces and cut things we don't care about. There's probably a lot that isn't worth keeping.

##### **Geohot** [[00:08:24](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=504)]
Keep the LLM tests. We should test both prefill and decode; the current numbers are only decode times. We should at least have modern LLMs.

##### **Chrism** [[00:08:40](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=520)]
Once the other tests run on our hardware, they should be under two minutes without a problem. I can probably get them under one minute if we want.

##### **Chenyu** [[00:09:01](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=541)]
Sounds good. Some of the benchmarks aren't very stable.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=550)]
The architecture is also bad because we have these large benchmark jobs. We should have many smaller runners, especially as we move to Docker and eliminate installation overhead.

##### **Chenyu** [[00:09:28](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=568)]
The slow ones are large jobs that are themselves slow.

##### **Geohot** [[00:09:35](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=575)]
Then those jobs need to be fixed. No job in tinygrad should take more than three minutes, especially with parallel compilation.

##### **Chrism** [[00:09:43](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=583)]
I can reduce the number of things each job does and lower the timeouts.

##### **Geohot** [[00:09:54](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=594)]
If an individual task takes more than three minutes, we messed something up.

##### **Chenyu** [[00:10:00](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=600)]
The openpilot supercombo compilation takes around three minutes.

##### **Geohot** [[00:10:06](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=606)]
That one can take three minutes, but that's the limit. We can run much more in parallel. Right now we have two NVIDIA GPU runners. The new setup will have eight one-GPU NVIDIA runners.

##### **Chrism** [[00:10:27](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=627)]
I think that makes more sense.

##### **Geohot** [[00:10:30](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=630)]
We can decide whether we want 24-gigabyte GPUs too, if that's useful.

##### **Chenyu** [[00:10:42](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=642)]
Sounds good. Speaking of parallel, let's move on to `PARALLEL`.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=648)]
Yeah. I didn't work on rangeify much this sprint. I ended up doing a bunch of quality-of-life improvements for comma.

##### **Chenyu** [[00:10:58](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=658)]
Is comma running a Qwen model?

##### **Geohot** [[00:11:01](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=661)]
No, comma's not running Qwen. Qwen is unrelated.

##### **Chenyu** [[00:11:05](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=665)]
They want parallel compile.

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=668)]
No, I mean Qwen is more for Chestnut people, right? To provide an application for Chestnut. Some guy was tweeting about how he got his 9600X and 7900 XTX to be fast with Qwen. Have you tried Qwen3.8-27B much?

##### **Chenyu** [[00:11:32](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=692)]
I tried it for like ten minutes. It's good for what it is.

##### **Geohot** [[00:11:41](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=701)]
Yeah. I mean, it's the first small model that's usable for anything, so I think it's an important one to run.

The two quality-of-life improvements I did for comma included parallel compilation. This is for everybody. Compilation now shares infrastructure with BEAM. When you have 20 kernels to compile, it does the lowering and compilation in child processes. It pickles the UOp, sends it across the process boundary, and sends back the compiled program. It also has a good progress bar with `DEBUG=1` that shows all the kernels it's building.

##### **Geohot** [[00:12:40](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=760)]
I don't think we need a full parallel graph rewrite yet, but you could imagine using the same infrastructure we have for `enter_calls=False` or `True`. We could have another option like `enter_calls=subprocess`, which automatically spawns a subprocess to do the CALL lowering because those calls can be treated as independent.

What I'm realizing is that the global and local ranges belong on the outer CALL. This is also how we express MULTI. That's unrelated to rangeify.

##### **Geohot** [[00:13:25](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=805)]
What else did I work on? I got the Qwen stuff merged yesterday. It merges basically three kernels: a linear kernel for a bunch of different GGML quant types, a Flash Attention kernel, and a Delta attention kernel, or whatever the thing is that Qwen and Kimi use. It more than doubles the speed compared to a BEAMed result.

I'd like to look at those kernels and figure out how we can improve the kernel API. I think that's a good level for a lot of people to write code at. It lets you express Flash Attention and all the memory-movement patterns pretty nicely, but you never have to think about things like orders being wrong, pointer arithmetic, or all the footguns that exist in CUDA. It should be able to get you almost all the speed.

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=858)]
The hardest thing to infer automatically seems to be loop orderings, and then shard sizes. I've been thinking about the scan op for Qwen. If you want to scan over something, it has to finish entirely, but there's no global barrier inside a kernel.

##### **Geohot** [[00:15:04](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=904)]
Because there's no way to express a global barrier inside a kernel, you end up with tricks that involve changing the axis orderings. That's very hard to infer and isn't easily expressed anywhere. Maybe in BEAM we have something called `SWAP`, but manually expressing the order in which you iterate over things and your blocking strategy gets you most of the speed. This is the Tile philosophy too.

I also spent a couple of hours this weekend reading Modular's `FastMatMul`. It's incredibly explicit. It's CUDA levels of explicit. It looks much more like an OpenCL replacement than anything else: OpenCL with Python syntax.

##### **Geohot** [[00:15:50](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=950)]
It's incredibly painful how you have to specify synchronization, asynchronous copies, and the exact matrix multiplier you're using. With that control comes extreme speed. cuBLAS gets 170 TFLOPS on a matmul, theirs gets 155, and BEAM tinygrad gets around 120 on a 4090.

##### **Geohot** [[00:16:52](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1012)]
I can work on rangeify more this week and hopefully start to get that stuff merged. I'm done with a lot of my side projects. Qwen is merged. My last side project is MI350P, which I have a PR for.

##### **Chenyu** [[00:17:14](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1034)]
Next, my stuff: weak `CONST` dtype. Last week I moved all the renderer changes. All the high-level changes are merged and everything down through the renderers is merged. There's now a middle block that's pretty much ready, but I want to merge it after the release, since we're supposedly doing a release.

After that is merged, all `CONST`s are weak. That's around 95% of the dtypes that no longer need to be UOp attributes. I started cleaning up the other things that still need strong, non-inferred dtypes on UOps and trying to reduce those use cases.

##### **Chenyu** [[00:18:16](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1096)]
After `CONST`, there are a few custom things where I can probably find a way to write them so the tests pass. `INDEX` is pretty much fixed. The code API is slightly annoying, and x86 and HCQ2 are the remaining offenders before we can remove dtype from UOp. x86 still depends on it a little, but I can probably work around that. It was using dtype specifically to store some information.

##### **Geohot** [[00:19:11](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1151)]
I'll be so happy when it's just gone.

##### **Chenyu** [[00:19:14](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1154)]
I think I'll merge `CONST`. There are some more cleanups I can do. A lot of late fusion for `CONST` and renderers wasn't working correctly. I tried to make sure the kernels weren't regressing, but some of it can now be covered by better tests. HCQ2 is very light, so it shouldn't be a big blocker.

I haven't spent time on the custom-code UOp because it seems quite flexible in what you can pass in and what dtype you expect from it. That's the remaining UOp that doesn't fit nicely.

##### **Geohot** [[00:20:09](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1209)]
For custom code, I'd be fine with putting a dataclass in the arg that includes a dtype. I don't think there's really another way to do that, and I think that's totally fine.

##### **Chrism** [[00:20:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1220)]
That makes sense.

##### **Chenyu** [[00:20:32](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1232)]
That's pretty much it for my part. We'll discuss the release later. The next item is HCQ2, which is related. We'll decide what we want to cut into this release. For `CONST`, I expect there might be some small weirdness, so I'd like to do the final flip after the release. It shouldn't matter much since we're doing a release anyway. With that, let's move on to HCQ2.

##### **Nimlgen** [[00:21:07](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1267)]
I've been working mostly on speed this week. HCQ2 enqueue time is sometimes better than HCQ1 and isn't worse for most things. But, yeah, there's the thing you posted in the channel.

There are a lot of copies. That's annoying because Python isn't an HCQ2 device, so it creates a lot of synchronization points between them. It's pretty slow: 288 copies and 289 HCQ2 batches because Python is a separate device.

##### **Geohot** [[00:21:58](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1318)]
It's not calling `realize` 288 times, though, is it?

##### **Nimlgen** [[00:22:05](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1325)]
No, it isn't.

##### **Geohot** [[00:22:08](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1328)]
You say Python isn't an HCQ2 device. Why not? Can we make it one?

##### **Nimlgen** [[00:22:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1346)]
We can. It's slightly annoying because, to make it HCQ, the pointers for the memoryviews have to be available to all the devices and potentially mapped to other devices. It's easy between Python and CPU.

##### **Geohot** [[00:22:49](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1369)]
This gets to another problem I've talked about in the theory channel. We need to separate the device that does the compute from the device where the memory lives. Python shouldn't have its own allocator. Python and CPU should have the same allocator. Python is just a compute engine.

##### **Nimlgen** [[00:23:23](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1403)]
Okay, we can do that.

##### **Geohot** [[00:23:27](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1407)]
This is a big project where we have to think about how to do it cleanly. Imagine two GPUs in a computer, with two buffers living on GPU 1. I should be able to add one to a buffer and store it in the other buffer, but do that add-one operation on GPU 2. There's no smart reason to do it, but the language should be able to express it.

##### **Nimlgen** [[00:24:04](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1444)]
It will kind of work already with the `Buffer` class.

##### **Geohot** [[00:24:14](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1454)]
It will work only because the buffer happens to be the same between two AMD GPUs. Think about this for Metal: Metal and CPU on a Mac shouldn't have different buffer types. We shouldn't add hacks for zero-copy. We should have memory devices and compute devices. SDMA itself is kind of a compute device.

I'm not totally sure what this abstraction will be yet. This is something we're going to work on, and hopefully we can have it by the end of the year. It's an important distinction, and I haven't seen another library really make it. The more you press on these abstractions, the more you realize that's what it has to be. If the problem is that data goes from Python to CPU to AMD, what does Python-to-CPU even mean? That shouldn't be a thing.

##### **Nimlgen** [[00:25:42](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1542)]
That's the problem. Between AMD and CPU devices, `Buffer` has the new `get_buf` function, which performs the underlying mapping and expresses the idea you're talking about. You can map the memory into different devices. That isn't implemented for Python, so HCQ does staging: it copies into CPU, after which CPU can map its buffer to any other HCQ2 device.

##### **Geohot** [[00:26:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1580)]
We have this concept that a memory device is visible to different compute devices. Python and CPU are identical and should share the same memory. Think about where the physical chips are. The CPU has some physical memory chips; to get the data to AMD, it has to go to the other chips.

There are multiple compute engines that can do that copy. I can copy it with a Python program, a C program, a GPU program, the GPU's SDMA engine, or, if I want to go absolutely crazy, a different GPU's SDMA engine.

##### **Nimlgen** [[00:27:11](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1631)]
The abstractions are bad currently, but it's already possible to express something like that between HCQ2 devices, just not with Python.

##### **Geohot** [[00:27:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1646)]
Where we eventually want to go is for there to be no such thing as an HCQ device; it should just be a device. All devices should fit in this framework. Then you have chunks of memory and things that do compute. This makes even more sense as we get into the MULTI world and have to be careful about where memory lives and how it moves.

When are we ready to delete HCQ1?

##### **Nimlgen** [[00:28:10](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1690)]
I also merged USB into HCQ2. It's pretty slow, and I need to iterate on it. Copy-in and copy-out are slow, especially after your recent changes made HCQ1 faster. I also ported QCOM.

##### **Geohot** [[00:28:39](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1719)]
You saw what I did to make HCQ1 fast, right? I don't love that it's expressed there. You could imagine expressing what I wrote as a TinyRed graph. Again, a USB device is actually a memory device. I want to get to the point where what I wrote is expressed as a TinyRed graph.

##### **Nimlgen** [[00:29:23](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1763)]
We have an initial USB implementation in HCQ2. I'll iterate on it to make it better and faster this week. I've also ported QCOM. I need some other changes, like the `NOLOCALS` stuff. Without `NOLOCALS` it's around 20 milliseconds; with it, 16 milliseconds.

##### **Geohot** [[00:29:54](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1794)]
Can you look into that? Put an LLM on it and see whether there's a three-line change we can make to the heuristics. I would love to delete `NOLOCALS`. It's an ancient optimizer that breaks the abstraction where, if you don't use BEAM, you don't need the device. Right now it's 20 milliseconds, up from 16, so it's 25% slower. If we can get it to around five milliseconds with a three-line heuristic change, let's just do that.

I'm not actually sure `NOLOCALS` itself is what's needed. It might just be the search.

##### **Nimlgen** [[00:30:53](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1853)]
That's right. But when I tried to replace `NOLOCALS` with BEAM, BEAM took much longer.

##### **Geohot** [[00:31:05](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1865)]
BEAM will be much slower because `NOLOCALS` isn't recompiling the thing. I think you might be able to put something into the heuristics.

##### **Chrism** [[00:31:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1880)]
Did BEAM take much longer to compile, or was the code BEAM output slower?

##### **Nimlgen** [[00:31:29](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1889)]
It took longer to compile.

##### **Geohot** [[00:31:32](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1892)]
Try the output code. See how fast it is compared to `NOLOCALS`.

##### **Nimlgen** [[00:31:44](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1904)]
I'll port NV. If we can cut the release this week, I can remove HCQ1 after the release.

##### **Geohot** [[00:31:56](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1916)]
I think that's a good plan.

##### **Nimlgen** [[00:32:03](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1923)]
We also have HEVC merged into our driver, and I have a working passthrough driver. I'm just cleaning it up.

##### **Geohot** [[00:32:19](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1939)]
I'd like to give that a try this week. I'll rent the DigitalOcean MI350X box for two hours. I think we can actually beat AMD's time now. The AMD GPU driver had a whole bunch of weirdness, so I hope our driver fixes it. I don't know whether it's our driver, because they're basically running the driver on the other side of that VFIO thing, right?

We still control the page tables? Good.

##### **Nimlgen** [[00:33:15](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=1995)]
That's it for me.

##### **Geohot** [[00:33:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2000)]
Sounds good. Next is GPT-OSS. How fast are we?

##### **Wozeparrot** [[00:33:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2006)]
We have a new fast run. We're at around 900 milliseconds per step now.

##### **Geohot** [[00:33:34](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2014)]
It looks good. I'm seeing three hours and 13 minutes.

##### **Wozeparrot** [[00:33:37](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2017)]
Three thirteen. I expect improvements to come a bit more slowly over the next few days because now it's a bunch of GEMM and other kernel optimization. Most of the fusion is done. There's still some MXFP4 transpose-quantize work that could be fused.

##### **Geohot** [[00:34:06](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2046)]
What's the speed on master?

##### **Wozeparrot** [[00:34:09](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2049)]
Master should be at last week's speed, around 1.2 seconds.

##### **Geohot** [[00:34:25](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2065)]
Good. We have a bit of buffer in the schedule. How many FLOPS are you getting from the GEMMs?

##### **Wozeparrot** [[00:34:39](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2079)]
The GEMMs are pretty bad. They're only around one PFLOP right now.

##### **Geohot** [[00:34:45](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2085)]
That's good. Is that MXFP4?

##### **Wozeparrot** [[00:34:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2088)]
No, FP8. We could go to FP4, which would improve things, but it isn't a simple change. I can't use the LLaMA MXFP4 GEMM because there's a bunch of MoE work in addition to the GEMM.

##### **Geohot** [[00:35:05](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2105)]
MoE work built into the GEMM? Whose GEMM are you using now?

##### **Chrism** [[00:35:15](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2115)]
HipKittens.

##### **Geohot** [[00:35:19](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2119)]
What's different about it from a normal GEMM?

##### **Wozeparrot** [[00:35:24](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2124)]
There's a bias term added to the output. Basically, it has a bunch of epilogue work attached to the GEMM.

##### **Geohot** [[00:35:33](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2133)]
How much does that matter if it's just two kernels?

##### **Wozeparrot** [[00:35:39](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2139)]
A decent amount. It also needs to be a grouped GEMM.

##### **Geohot** [[00:35:45](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2145)]
What's a grouped GEMM?

##### **Wozeparrot** [[00:35:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2148)]
It's a batched GEMM except the batches can be different sizes. You want to batch the GEMMs for all the experts so they do the matrix multiplies at the same time. You sort the tokens into buckets and then batch them along the axis.

##### **Geohot** [[00:36:24](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2184)]
Do you have a breakdown of the time?

##### **Wozeparrot** [[00:36:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2186)]
Yes. That's the current compute-time breakdown. We also have around 100 milliseconds of communications that aren't overlapped.

##### **Geohot** [[00:36:47](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2207)]
Those elementwise reduction kernels seem like the place to look.

##### **Wozeparrot** [[00:36:50](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2210)]
That's the next group to do. The MXFP4 transpose-quantize and the elementwise reduction should also be fused.

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2226)]
That makes sense. We need around 300 milliseconds more to hit the target?

##### **Wozeparrot** [[00:37:17](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2237)]
On compute, yeah. We're at 772 milliseconds of compute time right now, with non-overlapped communications on top of that. We need to drop around 300 milliseconds of compute time.

##### **Geohot** [[00:37:40](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2260)]
Or fix the communications. Is there any reason they can't be overlapped?

##### **Wozeparrot** [[00:37:46](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2266)]
No.

##### **Geohot** [[00:37:49](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2269)]
Maybe we'll learn something from the LLaMA improvements that we can use. Great, it looks like we're on schedule.

Are you following the MLPerf team? Anything we should be aware of?

##### **Wozeparrot** [[00:38:19](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2299)]
The leadership is changing.

##### **Geohot** [[00:38:30](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2310)]
Is the new leadership more or less in NVIDIA's pocket?

##### **Wozeparrot** [[00:38:43](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2323)]
They haven't said who the new leader is.

##### **Chenyu** [[00:38:47](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2327)]
There was an election or something, right?

##### **Wozeparrot** [[00:38:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2328)]
The founder is handing off the reins of MLPerf to a general manager.

##### **Geohot** [[00:38:55](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2335)]
Okay, cool. The founder is stepping down after eight years. It could be okay. Next is LLaMA.

##### **Qazalin** [[00:39:08](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2348)]
That's one hour and 57 minutes, as of yesterday. I fixed the bug that was causing it to converge more slowly.

##### **Geohot** [[00:39:25](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2365)]
Was that bug in GPT-OSS too?

##### **Qazalin** [[00:39:32](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2372)]
GPT-OSS doesn't use RoPE. The problem was that we were computing the RoPE frequencies in BF16.

##### **Wozeparrot** [[00:39:39](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2379)]
I looked at the PR and realized I had fixed this in GPT-OSS but never ported the fix to LLaMA.

##### **Geohot** [[00:39:49](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2389)]
It's fixed now. But two people have had this problem, so let's think about what we can do in general to detect things like this.

##### **Qazalin** [[00:40:09](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2409)]
I just diffed the recipe. I cloned NVIDIA's version and asked Codex what was different.

##### **Geohot** [[00:40:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2420)]
That seems fine. One hour and 57 minutes is exciting. We should stop thinking of AMD's time as our target and start thinking of NVIDIA's time as our target.

##### **Qazalin** [[00:40:36](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2436)]
I have all the times submitted to MLPerf. These are the B200 times and the AMD ones.

##### **Geohot** [[00:40:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2448)]
Got it. I want to break down the B200s. Is this our current breakdown on our GPU?

##### **Qazalin** [[00:41:04](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2464)]
B200s are fast. They have really good GEMMs. This is our current breakdown, with 45% MFU on the GEMMs, which is ridiculous. The shapes aren't favorable for that specific GEMM, so the setup cost and overhead aren't amortized well and we only hit around 40%. With a good shape it reaches 70%, so it's possible on this hardware.

##### **Geohot** [[00:41:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2508)]
I bet nobody optimized this. I see an unfused MXFP4 quantization. Why is it unfused?

##### **Qazalin** [[00:41:57](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2517)]
I wasted time on this one. It's unfused for two reasons. One is that there's an RMSNorm before it, and the dimensions and workgroups of that RMSNorm aren't favorable for the quantization. If you fuse the kernels, the total time is actually slower. There's no way to align the geometry nicely.

It can still be fixed. I think our real advantage over AMD will be modifying the GEMM assembly to include the quantization. That's also hard, but it's more possible because you aren't bound by the geometry.

##### **Geohot** [[00:43:03](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2583)]
You want to try to do it in the locals, right there with the GEMM? I don't think you can. What are you quantizing to MXFP4 from?

##### **Qazalin** [[00:43:22](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2602)]
FP32.

##### **Geohot** [[00:43:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2606)]
You're quantizing the data, not the weights?

##### **Qazalin** [[00:43:29](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2609)]
The weights too, for the inputs to the MXFP4 GEMMs.

##### **Geohot** [[00:43:45](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2625)]
Aren't we storing the weights in MXFP4? We don't have to re-quantize them, do we?

##### **Qazalin** [[00:43:55](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2635)]
No. We save them for the next pass. They quantize once and then they're saved. But the data has to be quantized each time.

##### **Geohot** [[00:44:12](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2652)]
Are you trying to put this in the input to the kernel or the epilogue of the kernel?

##### **Qazalin** [[00:44:24](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2664)]
The input.

##### **Geohot** [[00:44:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2666)]
That's really hard. Remember that you're accessing each input N times. For each input to a GEMM, whether data or weights, if you're multiplying two N-by-N matrices, you're accessing each thing N times. Trying to do anything in the prologue of a GEMM isn't really going to be possible.

Especially if you're doing something that shrinks. If you're doing something that expands, it's often worth it because of memory bandwidth. But you don't want to read FP32 N times; it's almost always going to be slower. Anything you can do in a GEMM epilogue is great.

##### **Qazalin** [[00:45:23](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2723)]
I've fused whatever I could, but the remaining quantization is still around 40 milliseconds.

##### **Geohot** [[00:45:38](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2738)]
How much of this is on master?

##### **Qazalin** [[00:45:40](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2740)]
The all-reduce work isn't on master. Last week I also changed everything to assembly. The custom assembly kernels, including Flash Attention and the BF16 GEMMs, aren't merged because the assembly is too long. I have to go through it meticulously and clean it up.

##### **Geohot** [[00:46:15](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2775)]
What do you mean the assembly is too long? Why do we care how long it is?

##### **Qazalin** [[00:46:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2786)]
It's thousands of lines long. It won't be very readable or understandable. I literally copied the code objects into Python.

##### **Geohot** [[00:46:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2808)]
I see. The diff is too big to render. If that's what it is, that's what it is. I think it's fine to merge it in `extra`; I'm not worried about the number of lines there.

This seems like good progress. We should plot our times per week. I think our target is one hour and 22 minutes. Imagine if we could beat NVIDIA in the next MLPerf.

##### **Qazalin** [[00:47:41](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2861)]
That would be cool. This is what it takes to cut one hour from the time. Compared with where we were two months ago, it's crazy to see.

##### **Geohot** [[00:47:57](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2877)]
Are you running with HCQ1 or HCQ2?

##### **Qazalin** [[00:48:01](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2881)]
I'm not using HCQ2 because there's no all-to-all.

##### **Geohot** [[00:48:05](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2885)]
I saw a PR for that, but I'm not sure whether it was merged.

##### **Qazalin** [[00:48:17](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2897)]
I thought it had merged. I'll try it.

##### **Nimlgen** [[00:48:30](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2910)]
It isn't merged yet. I can merge it, and it works with HCQ2.

##### **Geohot** [[00:48:36](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2916)]
LLaMA is our most demanding application, so it's good to stress HCQ2 with it. What do you think we can get to next sprint?

##### **Qazalin** [[00:48:50](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2930)]
I'll work on idle time. We still have some, but it's down to around 29 or 30 milliseconds.

##### **Geohot** [[00:49:04](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2944)]
I see, compute-time idle. That isn't much. The real win seems to be in those bad MFUs at the top. That's probably better to work on than the last 30 milliseconds of idle time.

How good is `VIZ=2` on this chip?

##### **Qazalin** [[00:49:43](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=2983)]
`VIZ=2` doesn't work because CDNA's SQTT isn't ideal. I'm not sure fixing that will solve the kernel problem, because LLMs are really bad at writing assembly.

##### **Geohot** [[00:50:05](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3005)]
Maybe we start working backwards. You've written the kernels in our assembly dialect. Can we use our register allocator?

##### **Qazalin** [[00:50:33](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3033)]
You want something like PTX?

##### **Geohot** [[00:50:36](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3036)]
Literally just before PTX. Take their assembly and leave it exactly as it is, strip out all the registers, and use our register allocator. Do we get a better time, a worse time, or incorrect output?

Then we start working backward to a higher-level dialect. After register allocation, we start removing instruction selection and using our instruction selector. How much instruction deselection can we do?

##### **Qazalin** [[00:51:39](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3099)]
Doesn't every higher abstraction level lose more performance? Isn't the ultimate thing to handwrite everything?

##### **Geohot** [[00:51:57](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3117)]
I think the opposite is probably true. My guess is that our register allocator will be better than the handwritten work.

##### **Raine** [[00:52:11](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3131)]
Can I say something? Our register allocator isn't really optimized for GPU architectures yet. I was going to leave that until after the backend was merged. It's just linear scan. We should try to copy LLVM, which prioritizes allocation by spill size, so it allocates wider register values first.

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3156)]
I wouldn't copy LLVM. I would use ILP. The first question is whether our register allocator is correct, and then whether it's better. Linear scan probably won't outperform handwritten assembly, but humans are bad at register allocation. They're bad at carefully tracking the liveness of everything and solving that global optimization problem. We can solve it with a global optimizer, and that's what we should move our register allocator to.

##### **Raine** [[00:53:21](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3201)]
That paper looked really cool. I'd like to add something like that once the backend is merged.

##### **Geohot** [[00:53:27](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3207)]
I don't want LLVM-style hacks where we say, "This is a large allocation, so it goes in the large-allocation bucket."

Register allocation is something humans are bad at when writing assembly. Humans are pretty good at linearization. They don't view things as a topological sort over a whole graph; they think linearly about how to keep every slot of the GPU occupied. Humans and LLMs are good at that local problem, and both are bad at the global problem. If we move register allocation out, eventually our dialect will be high-level enough that LLMs are really good at it.

##### **Qazalin** [[00:54:37](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3277)]
It's plausible. I'll look at it.

##### **Geohot** [[00:54:40](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3280)]
If we want to reach NVIDIA's time, we'll have to improve. We won't do it with AMD's kernels. Two hours isn't even the target anymore; now it's more like an hour and 30 minutes.

##### **Qazalin** [[00:55:13](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3313)]
Yeah. That's how I can get out of assembly, because our LLMs are really bad at it. I'm hoping it's fixable.

##### **Geohot** [[00:55:26](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3326)]
Do you think the MI350P machine would help you? You could have LLMs grind on kernel performance without worrying as much.

##### **Qazalin** [[00:55:47](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3347)]
So it doesn't get discovery signature mismatch?

##### **Geohot** [[00:55:51](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3351)]
It reboots in ten seconds. Don't worry, it still has all the other problems. It can't fully reset because the kernel can't reset it either. If you load and unload the AMD GPU driver, it crashes around one in three times.

I'll try to get that merged today and give everyone access to the machine. You can use it to grind kernels. It's half the chip: the same chip, but half the XCDs don't work. That shouldn't matter for the work you're doing. It has half the memory bandwidth, and it all scales correctly. If you improve performance on the MI350P, the same kernel should translate perfectly to the MI350X.

##### **Chenyu** [[00:57:01](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3421)]
Let's quickly go through the release. Are we good to release? Do we want to release with HCQ2 or not?

##### **Geohot** [[00:57:13](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3433)]
No on HCQ2. We'll leave it behind a flag. That was the verdict.

##### **Chenyu** [[00:57:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3440)]
Now it's off by default?

##### **Geohot** [[00:57:22](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3442)]
Yeah, off by default.

##### **Chenyu** [[00:57:24](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3444)]
Everything looks good from my end, and if JIT looks good now, since that's a major overhaul for the release, I think we're good. Are we tagging a release?

##### **Wozeparrot** [[00:57:40](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3460)]
Yes. I'll tag it today.

##### **Chenyu** [[00:57:46](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3466)]
Is there anything Qwen-related or Chestnut-related that we want to double-check?

##### **Geohot** [[00:57:54](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3474)]
I think it's in a pretty good state. I got the Qwen work merged yesterday, and I've been testing it for a long time. I don't think there's anything wrong with it.

##### **Chenyu** [[00:58:04](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3484)]
B1TG said there was something wrong with the variable. Does that affect it?

##### **Geohot** [[00:58:11](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3491)]
I fixed that. I see B1TG typing in case there's something I missed, but I fixed the variable issue. It was my bug.

##### **Chenyu** [[00:58:23](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3503)]
We'll wait to see whether he has anything to say. Otherwise, I think we're good for the release. We should tag it after the meeting.

Anything for RDNA3 that you want to discuss quickly?

##### **Raine** [[00:58:50](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3530)]
I think it should be ready for review this week. I added VGPR and SGPR spilling, added a small lowering pass for register buffers that fixes the regalloc logic, and removed all the bad optimization slop I had in there.

I have one failing test. Once again, it's a different test: a `tan` regression caused by subregister spilling, which I'll fix today. There are also some tensor-core regressions that I should fix. I've tested it on hardware recently, and everything looks good.

##### **Chenyu** [[00:59:24](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3564)]
A quick comment on the `CONST` and casted-`CONST` work: I tried very hard not to union them. A `CONST` will either be a weak `CONST` or be cast to some strong dtype. I tried not to mix the two in a `UPat`. It's easy to write an OR pattern over casted and plain `CONST`, but most of the time you need only one, and we shouldn't waste work by mixing them.

##### **Raine** [[00:59:59](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3599)]
That wasn't a good idea of mine. Sorry, I shouldn't have tried to do that.

##### **Chenyu** [[01:00:04](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3604)]
It's okay. My AI tries to do that all the time too.

If you're reading the value, handling both is much more reasonable. You don't want to write a lot of logic saying, "If it's a cast, take source zero; otherwise, test whether it's a `CONST`." If you're reading the value of such a node, it's okay to have a helper that just reads the value. But don't put that union in a `UPat`.

##### **Chenyu** [[01:00:45](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3645)]
Is comma happy? I saw Yassine working on a disk-cache change.

##### **Geohot** [[01:00:57](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3657)]
I don't know about the disk cache, but comma uses it with threads and there's a threading bug now. I merged his first PR, which looked correct, but it caused a race condition in `multiprocessing.spawn` that I don't understand. I don't like his second PR because it puts locks on the hot path.

##### **Chenyu** [[01:01:18](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3678)]
I'll leave that to you.

##### **Geohot** [[01:01:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3680)]
I'll deal with it. I got his other PR merged.

##### **Chenyu** [[01:01:23](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3683)]
Sounds good. I think that's pretty much it. Is everyone happy with Kimi?

##### **Geohot** [[01:01:35](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3695)]
It was flaky last night. Does anyone know why?

##### **Chrism** [[01:01:39](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3699)]
Flaky how?

##### **Geohot** [[01:01:42](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3702)]
It was just going down.

##### **Chrism** [[01:01:45](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3705)]
Yeah, it went down Friday night too.

##### **Geohot** [[01:01:48](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3708)]
Interesting. I saw something about the driver being stuck. I don't know what that means.

I think that's it for this meeting. Anything else?

##### **Chenyu** [[01:02:11](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3731)]
That's it. We'll tag a new release. Which version are we on now, 0.13?

##### **Geohot** [[01:02:20](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3740)]
I think 0.14.

##### **Chenyu** [[01:02:23](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3743)]
Wow. Okay, nice. Thank you, everyone. See you next week. Bye-bye.

##### **Geohot** [[01:02:32](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3752)]
Bye.

##### **Chrism** [[01:02:32](https://www.youtube.com/watch?v=2CIBfxmsyLI&t=3752)]
Bye.
