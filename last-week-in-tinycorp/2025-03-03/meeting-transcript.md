# 2025-03-03 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time (10pm HK time)
- company update
- torch frontend (mnist, nano_gpt, test_ops, torch.compile, multi gpu, interop)
- quantize devec, fast gemm amd
- bert, rand, fuse_arange
- schedule become_map
- drivers, interop
- WebGPU (tinychat, export)
- onnx
- amx tensor core
- retinanet
- remove-comgr

### Audio

[Youtube Link](https://www.youtube.com/watch?v=hIWzGyEX2do)

### Highlights

- [Company Update](#geohot-000006) New Hong Kong office from March 10 to April 10. Intel MAX 1450 GPUs are arriving.
- [Torch Frontend](#geohot-000403) MNIST and ResNet inference work. NanoGPT has a memory leak but is being fixed.
- [Multi-GPU & Torch Compile](#geohot-000909) Skeleton for Torch Compile exists, needs cleanup. Memory interop for TorchTensor and TinyTensor is merged.
- [Fast GEMM & Quantized Devec](#geohot-001234) Fast GEMM achieves 40 TFLOPS; quantized devec optimizations improve performance.
- [BERT & Fused Random](#chenyu-001945) First sub-four-hour BERT run. Working on FUSE_ARANGE to make RAND a single kernel.
- [Scheduler & Memory Profiling](#qazalin-003415) Merged cast-before-view and fast-viz. Working on caching, profiling expands, and becomes map.
- [Tenstorrent Backend Bounty](#geohot-001812) Bounty for adding Tenstorrent support with multiple backers.
- [AMX Tensor Core](#ignaciosica-005304) Refactoring `define_acc`, `load`, and `store` for AMX support.
- [RetinaNet](#flata-005502) Running on six GPUs, but utilization is low. Evaluating hyper-parameter tuning.
- [Remove COMGR](#b1tg-010029) LLVM 18/19 backend works, but REMU lacks some instruction support.
- [TinyChat & WebGPU](#hooved-004819) TinyChat PRs are ready for review.

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=hIWzGyEX2do&t=0)]
Let's start with any company update?

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=0)]
Yes, I think we got an office in Hong Kong from the 10th for a month.
So from March 10th to April 10th.

##### **Chenyu** [[00:00:16](https://www.youtube.com/watch?v=hIWzGyEX2do&t=0)]
I need to extend that for another two weeks.
It will be later.

##### **Geohot** [[00:00:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=21)]
Another two weeks.
Oh, well, I'm not sure I'm going to be here after April 10th.

##### **Chenyu** [[00:00:22](https://www.youtube.com/watch?v=hIWzGyEX2do&t=22)]
But you are not?
OK, let's discuss it offline.

##### **Geohot** [[00:00:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=22)]
Yeah, we can discuss this offline.
Yeah, yeah.
Well, I have to make it back to San Diego.
But yeah, so we have a big office.
We've got a bigger office this time.
We've got this nice coworking space.
So if anyone is interested in a job, solve some bounties quickly, come out to Hong Kong, hang out with us.
Yeah, we're mostly a remote company, but we sometimes get together in person.
We have in-person stuff in San Diego and in-person stuff in Hong Kong.
So, yeah.
I think we'll be able to extend it, though.
We'll see.
I got a very good deal because I only booked it for one month.

##### **Chenyu** [[00:01:24](https://www.youtube.com/watch?v=hIWzGyEX2do&t=22)]
Interesting.
Isn't it usually the case that if it's shorter, it's more expensive?

##### **Geohot** [[00:01:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=22)]
Well, yeah, but they have a lot of empty offices in this building, so I got a really good deal.
The other company update is Intel actually came through.
Justin Long from Intel actually came through, and we got some samples.
So we have two MAX 1450s and a MAX 1100 on the way, potentially with a lot more MAX 1450s to follow up.
Intel did make big GPUs.
They just didn't sell them as consumer GPUs.
The MAX 1450 is, again, the software is going to need a lot of work, but from a hardware perspective, it's as good as an H100, so.
Somewhere between A100 and H100.
But yeah, so if the stars align, we'll be able to purchase a lot of them, build some blue TinyBox pros.
Yeah, and if they don't, well, the AMD stuff looks OK.
The new AMD stuff looks OK.
Samples are real.
We'll bring them up in computers.
We'll start to play with them.
It really is.
They're really our sweet GPUs.

##### **Chenyu** [[00:03:09](https://www.youtube.com/watch?v=hIWzGyEX2do&t=161)]
Sounds good.
OK.
That's the company update.
Let's move on to Torch as a frontend.
I think it's a
We have new, I don't know, for the new people here, this is a project that, uh, you can write torch code and with I think two lines.
You can use tinygrad for its device or for its backend.
And, uh, your torch code will run on tinygrad, which run on the devices that tiny support.
So.
Definitely not in nanaGPT.
I think MNIST works now?

##### **Geohot** [[00:04:03](https://www.youtube.com/watch?v=hIWzGyEX2do&t=238)]
MNIST works.
ResNet works.

##### **Chenyu** [[00:04:08](https://www.youtube.com/watch?v=hIWzGyEX2do&t=238)]
ResNet inference work.

##### **Geohot** [[00:04:11](https://www.youtube.com/watch?v=hIWzGyEX2do&t=238)]
NanoGPT kind of works.
It's using a lot of RAM, but we don't know why.

##### **Chenyu** [[00:04:18](https://www.youtube.com/watch?v=hIWzGyEX2do&t=238)]
Oh, no.
There's an update on the PR.
Oh.

##### **Geohot** [[00:04:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=261)]
You know what?

##### **Chenyu** [[00:04:22](https://www.youtube.com/watch?v=hIWzGyEX2do&t=262)]
There was a memory leak.

##### **Geohot** [[00:04:25](https://www.youtube.com/watch?v=hIWzGyEX2do&t=265)]
Great.
Have we fixed that?
I think he said there's a tmp, like, workaround or something.

##### **Geohot** [[00:04:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=265)]
He's a speaker.
He wants to say something.
Oh, I see.
Yeah, cool.
Yeah, I think this is on the right track.
I think we fixed this.
We fixed whatever the memory leak is.
And we don't need to.
I don't think implementing AMP is part of it, but I think fixing the memory leak is part of that.
When we're done with the Torch front end, it's going to be zero overhead.
So there's no downside to using Torch as a front end.
Once it's in TinyGrad at all perfectly, you get all the same speedups.
It's not like the Torch thing is going to be really slow.
So yeah, it's going to be a good front end.

##### **Chenyu** [[00:05:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=265)]
What do we want to handle for things that we don't support?
Say, the things that has data-dependent shape.

##### **Geohot** [[00:05:32](https://www.youtube.com/watch?v=hIWzGyEX2do&t=265)]
Oh, I mean, data-dependent shape.
Yeah.
I mean, those have to be graph breaks.
We can support them, but they're graph breaks.

##### **Geohot** [[00:05:46](https://www.youtube.com/watch?v=hIWzGyEX2do&t=346)]
Like, it's going to realize and stuff.
I think that's fine.
But yeah, we shouldn't really have much data-dependent shape stuff.
But yeah, things like TopK, I mean, we just need to implement.

##### **Chenyu** [[00:05:57](https://www.youtube.com/watch?v=hIWzGyEX2do&t=357)]
TopK is fine.
It's more like zero and some mask select thing.

##### **Geohot** [[00:06:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=357)]
Yeah, I mean, there's no reason we can't get test ops working first.
Like, oh, test ops obviously has to work, because it works in Tinygrad.

##### **Chenyu** [[00:06:12](https://www.youtube.com/watch?v=hIWzGyEX2do&t=357)]
Well, it's making good progress.
Last time I saw, there was only 10 failure.
I don't know what the number is now.

##### **Geohot** [[00:06:23](https://www.youtube.com/watch?v=hIWzGyEX2do&t=383)]
Great.
I think there's some progress on multi-GPU, too.
Yeah.

##### **Chenyu** [[00:06:34](https://www.youtube.com/watch?v=hIWzGyEX2do&t=383)]
So Torch Compile, I think.

##### **Geohot** [[00:06:40](https://www.youtube.com/watch?v=hIWzGyEX2do&t=400)]
I wrote a skeleton for it, if someone can clean that up.
I mean, you don't really have to do anything that different with Torch Compile.
The only thing Torch Compile really does is runs the Torch function decorated with the TinyJit.
Torch Compile also takes care of all the PyTree stuff for you.
So it works really nicely with TinyJit.
That just needs to be cleaned up a little bit more.

##### **Chenyu** [[00:07:09](https://www.youtube.com/watch?v=hIWzGyEX2do&t=429)]
How does that work?
We need to update our JIT so that it's not running like different things the first time and the second time.

##### **Geohot** [[00:07:18](https://www.youtube.com/watch?v=hIWzGyEX2do&t=429)]
We can make the compile not have overhead.
So like right now the compile runs it three times.
Eventually, I want to update our JIT not to do that, but I think just running it a few times is not that big of a deal either.
We can also just not run it in the compile, and it can only be fast on the third time of compile.
It's just important that compile actually decorates it with the tiny JIT and gets the inputs and outputs to be expanded, which Torch Compile does for you.

##### **Chenyu** [[00:07:50](https://www.youtube.com/watch?v=hIWzGyEX2do&t=470)]
Yeah, I think that is also going.
And finally, the memory interrupt.
No, the memory interrupt for TorchTensor and TinyTensor.

##### **Geohot** [[00:08:10](https://www.youtube.com/watch?v=hIWzGyEX2do&t=470)]
Oh, yeah.
Yeah, I think that's merged.
I think Nimlgen did merge that.
You can just do dot from blob on a CUDA, and you can import it.
So if you have TorchCUDA, you can import that from memory.

##### **Chenyu** [[00:08:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=470)]
OK, sounds good.
Yeah, so I think the immediate next step is multiple bounties that.
I think this direction, somehow a lot of new people are contributing.
So that's always nice to have, nice to see.
And do we have any?
Let's get the feature to be more complete, then we can think about the speed issue on this.
Is there any other popular Torch script or Torch things that people run that we also want to run?

##### **Geohot** [[00:09:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=561)]
NanoGPT and hlbcifar are.
I think FastGPT is another one.
I think all of these common Torch things.
I went through all the Torch examples and tested them.
Most of them worked.

##### **Chenyu** [[00:09:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=569)]
Oh, someone mentioned
Someone mentioned the stable diffusion large can work with comfy UI.
So now you can use the comfy UI workflow and use tinygrad to run the imagegen models.
I thought that was pretty cool.

##### **Geohot** [[00:09:49](https://www.youtube.com/watch?v=hIWzGyEX2do&t=589)]
Great.
Yeah, it shouldn't be slow either.
The back end should be pretty decent.

##### **Chenyu** [[00:09:58](https://www.youtube.com/watch?v=hIWzGyEX2do&t=598)]
What happens if a Torch project uses Triton or CUDA binding?

##### **Geohot** [[00:10:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=605)]
Well, so it doesn't use, that's not going to work.
Yeah, it doesn't use triton or CUDA.
It's tinygrad, it's totally separate.
Like if you're using triton or CUDA, you're using the CUDA backend, you're not using the tiny backend.
tinygrad is like a new device.
You do like.tiny, device = tiny, all that stuff.
So if you want raw CUDA, you're going to have to do it using like tinygrad's abstractions,.torch's abstractions.
But yeah, for now, that stuff's not going to be supported.

##### **Chenyu** [[00:10:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=634)]
Yeah.
And are we going to support it?
Probably no.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=hIWzGyEX2do&t=648)]
Probably no.
I mean, I could see a world in which we support something like a custom kernel.
that can go in our graph.
And then maybe for things like flash attention, it could work.
But this is not anytime soon.
Maybe someday, but not anytime soon.

##### **Chenyu** [[00:11:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=648)]
Yeah.
For now, we are using what Torch expressed.
It's a layer of about, I don't know, 200 functions.
And the idea is if we implement those functions using tinygrad code, then it kind of just works.
Any custom stuff or any combining won't work anytime soon.
OK.
That's it for Torch frontend.
So action item for people here, you can find your favorite Torch script that's written in Torch and add those
Install TinyGrad, add the three line change to the project, basically move all your tensors to device tiny, and see if it works.
If not, just go somewhere.

##### **Geohot** [[00:12:08](https://www.youtube.com/watch?v=hIWzGyEX2do&t=648)]
Yeah, if it's like a normal Torch project and you want to post an issue, we'll look into it.

##### **Chenyu** [[00:12:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=737)]
Great.
OK.
Let's move on.

##### **Chenyu** [[00:12:28](https://www.youtube.com/watch?v=hIWzGyEX2do&t=748)]
Quantize devec?
I guess fast gemm, because you do something.

##### **Geohot** [[00:12:34](https://www.youtube.com/watch?v=hIWzGyEX2do&t=748)]
Yeah, stream this weekend with fast gemm.
The quantized devec is something that I've been working on for the DSP, but I'm finally just doing it right.
So this is something that's been wrong the entire time.
Basically, to do load store grouping, I was doing the load store grouping on loads and stores.
but now we have this index UOp, so I've moved it to the index UOp.
It's faster.
We get about a 5% speed up to everything by doing it this way.
And then we also don't have to de-vectorize.
We might not have to de-vectorize anything.
With the DSP, you can't de-vectorize.
Maybe you can de-vectorize the indexing, but if you de-vectorize the actual math,
it will never be fast.
You have to keep things in 128 element vectors.
So I wrote this whole thing to re-vectorize, and then I'm like, this is stupid.
We just need to never de-vectorize.
So that's what this new, it's basically just, it's called expand index.
And what it does is if you're loading from memory addresses,
0, 1, 2, and 3, it groups them together into a float4 load.
And it does this without needing to see the loads, but it does this while it's still in indexing.
So it's faster.
It's cleaner.
And it allows you to keep all the math still vectorized, which with some backends like LLVM and Clang just totally works fine.
So it makes rendering the kernels a lot faster.
It gives LLVM and Clang hints to do things.
So it should just be way better.
I got most of the bugs fixed.
I have a few minor things with image still to deal with, stupid image.
But every time, the hacks for image get a little bit smaller.
So that's good.

##### **Chenyu** [[00:14:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=869)]
Great.
Speaking of image, do you see comma, like, a bit cleanup because TinyGrad?

##### **Geohot** [[00:14:42](https://www.youtube.com/watch?v=hIWzGyEX2do&t=869)]
Oh, are they using TinyGrad in CI for CPU?

##### **Chenyu** [[00:14:45](https://www.youtube.com/watch?v=hIWzGyEX2do&t=885)]
Yeah, yeah.

##### **Geohot** [[00:14:48](https://www.youtube.com/watch?v=hIWzGyEX2do&t=888)]
Oh, that's great.
Yeah, I mean, once you're in TinyGrad, it kind of runs everywhere.
So that's great.
I'm glad to hear they're relying on it more.
And our dream is to get Comma to switch to TinyGrad for training.
But now, it could just kind of work with the Torch backend.

##### **Chenyu** [[00:15:11](https://www.youtube.com/watch?v=hIWzGyEX2do&t=888)]
We should get their Torch code and see if it runs.

##### **Geohot** [[00:15:15](https://www.youtube.com/watch?v=hIWzGyEX2do&t=888)]
Yeah.
I mean, this is especially going to be interesting if the Intel thing works out.
If the Intel thing works out, Comma's about to get a whole lot of Intel GPUs.

##### **Chenyu** [[00:15:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=935)]
How fast was the gen.

##### **Geohot** [[00:15:38](https://www.youtube.com/watch?v=hIWzGyEX2do&t=938)]
So I mean, I copied his stuff in exactly.
So if you use his assembly, you get 40 tflops.
So it's like twice as fast in what's in TinyGrad now.

##### **Chenyu** [[00:15:49](https://www.youtube.com/watch?v=hIWzGyEX2do&t=938)]
Oh, that's for Float32?

##### **Geohot** [[00:15:52](https://www.youtube.com/watch?v=hIWzGyEX2do&t=938)]
Flow32, yeah.

##### **Chenyu** [[00:15:54](https://www.youtube.com/watch?v=hIWzGyEX2do&t=938)]
Okay.

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=938)]
Yeah.
So it's like twice as fast in what's in TinyGrad.
It's like 40% faster than what's in Rocm.
So I basically just extracted the tricks.
The main trick that we're not doing in TinyGrad is we're not using shared memory.
We're not using.. It's called like shared in CUDA, but it's like the local memory.
We're not first copying the stuff into SRAM.
Uh, so I want to finish the quantized stuff and then I want to add that as a search.
I want to add that to BEAM.
Uh, I mean, I was like messing around with like trying to do it by hand, but I'm like, no, I just need to like write this correctly, add it to BEAM 
BEAM will find it.
Then there's that optimization.
Then there's the double buffering optimization.
And then our jit should be 40 giga flops.
And that'll be faster than, uh, than rocm.
It should be fast.

##### **Chenyu** [[00:16:45](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1002)]
So yeah, that's good.
You have four more weeks for the contract?

##### **Geohot** [[00:16:53](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1002)]
Yeah, yeah, yeah.
We have till the end of March for the DSP contract.
I really got to work on that.
Yeah, it's hard.
The DSP represents the pinnacle of difficulty.
I talked about this a bit on stream.
It's SIMD and not SIMT.
So you actually have to deal with all your loads in stores in a vectorized manner.
And then you're using shuffle units to put things in the right place.
Whereas GPUs, you never have to think about any of this.
You can just do 32 different loads, and the memory coalesce, or it'll either hit or miss.
So yeah, it's a lot easier to get performance on a GPU than it is a Qualcomm DSP.
But if we can get performance on the DSP, it's looking really good for everything else.

##### **Chenyu** [[00:17:45](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1065)]
Sounds good.
OK.
Before moving on to my stuff, I want to ask about tenstorrent.
I wrote attention in SRAM on the tenstorrent paper, implementing Alpha 4.3 on tenstorrent wormhole.

##### **Geohot** [[00:18:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1065)]
Where is this?

##### **Chenyu** [[00:18:08](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1065)]
In the reds-only VC chat.

##### **Geohot** [[00:18:12](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1065)]
Oh.
Any update on tenstorrent support?
I mean, we have a bounty for it.
tenstorrent has backed up.
tenstorrent has backed up our bounty.
corsix has backed up our bounty.
So you can make some good money if you actually support tenstorrent's cards.
With all the people supporting it, it looks almost like you're going to make like $5,000, $6,000.

##### **Chenyu** [[00:18:36](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1065)]
And now with torch as frontend this will be extra useful for everyone, I think.

##### **Geohot** [[00:18:41](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1065)]
Yeah.
So TinyGrad basically, like, we should have done, like, Torch's frontend was such a good idea.
If you implement a Tiny backend now, you're going to get Torch, ONNX, and TinyGrad.
And you're going to get the other ones.
Like, Torch and ONNX are basically free.
So.
But, yeah.
Someone's got to do the tenstorrent backend.
Moritz, if you wrote the paper, I mean, it sounds like you should do it.

##### **Chenyu** [[00:19:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1157)]
Yeah.
I think for now, it's a thing that we can incentivize through bounty, but not a thing that we actively are trying to do.

##### **Geohot** [[00:19:31](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1157)]
Yeah, we don't have internal company resources to put on it.
But I'm happy to put a few thousand dollars up for it.
It'd be cool to do.

##### **Chenyu** [[00:19:45](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1157)]
OK.
Let's move on.
for BERT, we have our first sub four hours run, so three hours something.
There are something, so for now, the run is about four hours green, and I think five and a half on red.
So red are a little bit slower.
I was trying the SDMA bind thing that Nimogen suggested, but I keep crashing.
It crashed my machine.

##### **Geohot** [[00:20:22](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1157)]
It's only crashing with bind.

##### **Chenyu** [[00:20:25](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1157)]
So far, yes.
It crashed twice, and these things only crash after a few hours.

##### **Geohot** [[00:20:36](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1157)]
Nimlgen, can you explain what SDMA bind is?

##### **Nimlgen** [[00:20:43](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1157)]
So yeah, basically it uses indirect execution on these daemon queue.
So yeah, we're just not, yeah.
But actually I think that's, you know, just trying to, I think like it's a bit deeper problem and not related to these daemon, like indirect execution.
I've noticed it several times.
I think it's something with the,
ordering like how like what data is sent to the GPU and what GPU sees because first of all the main difference is that we use queues which are
So only for AM, we use queues which are physically allocated on the GPU.
Not on the system RAM, but on the GPU.
So when we need to write into the queue, we just push into the device, and not device pulling from the system queue.
And I'm not sure that it's.. That's the main difference with the AMD backend.

##### **Geohot** [[00:21:57](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1317)]
And is there any reason we do it differently?
Is there any reason we don't just use System ram?

##### **Nimlgen** [[00:22:09](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1329)]
Actually, I think that it's just because we just know that we cannot think about caches on the system level.
But yeah, maybe we have to switch it.

##### **Geohot** [[00:22:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1329)]
Now you have to think about caches on the GPU, right?
If you do it right to the GPU,
Does that actually end up in the RAM?

##### **Nimlgen** [[00:22:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1355)]
That's kind of strange, because they tried to implement the same feature in the rocr runtime, and it's still on the block, and there are some issues that it doesn't work for them as well.
I don't know, maybe it's something with the GPU missing, because
For these features, actually, you need interrupt handler to be enabled on the GPU.
So if it's not enabled, interrupt handler is somehow important for this part.
And yeah, if it's not enabled, it will hang at the same time.

##### **Geohot & Nimlgen** [[00:23:15](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1395)]
I mean, it should just basically be a one line change to throw it in pinned memory on the CPU instead of GPU memory, right?
Yeah.
So we already have this flag to do this.
Got it.
I mean, we really should, we should be fuzzing this.
Like we should be able to, we shouldn't be finding things like this on a BERT run.
We should find things like this in a fuzzer.
Yeah.
I mean, yeah, I know about this problem and we have fuzzers.
So just to send these signals, I think it was fine for like several dozens of hours.
But I think it's also related to the size of the queue and how it's related to the size of the queue.
Let's figure out.
I think top priority is figuring out how to get our fuzzer to replicate this crash.
Any data we have on the crash or anything.
Let's get this replicated in our fuzzer, and let's truly root cause this.
Because right here is where we have the ability completely outshine AMD.
We can root cause this.
We can figure out exactly what's going on, and we can fix it.
And then we can write regression tests such that it never happens again, regression fuzzers such that it never happens again.
This is the highest priority, and this right here is why we need AMD.

##### **Geohot** [[00:24:41](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1481)]
We can do this.

##### **Chenyu** [[00:24:50](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1490)]
OK, for now, the best report I can give you is SDMA bind equals to 1.
And it crashed for me twice, but it's only after five hours.
I don't know.
I think I can try different stuff if I have any instructions for me, like some debugging flags or something.
Maybe I can log more stuff.

##### **Geohot** [[00:25:23](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1490)]
I would also just like, the way that I would probably go about this is take BERT and just say, OK, what if we don't run any of the compute kernels?
Does it still happen?

##### **Nimlgen** [[00:25:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1535)]
Yeah.
So yeah, not exactly for the eSIM, I think.
But OK, yeah, I just.
OK, yeah, that makes sense.

##### **Chenyu** [[00:25:52](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1552)]
Does the fuzzer cover multi-GPU?

##### **Nimlgen** [[00:25:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1552)]
Yeah.

##### **Chenyu** [[00:25:57](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1552)]
OK.

##### **Nimlgen** [[00:25:58](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1552)]
So it's basically like the fuzzer, I'm just fuzzing signals there.
Because we have, yeah.

##### **Geohot** [[00:26:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1552)]
I think we got to try, like, my guess would be that there's some cache that's not coherent here.
That there's some, like, I know PCIe has a cache.
I know the GPU has caches all over the place.
I mean, I don't even know really what's doing the reading of these queues.
Does that thing have a cache?

##### **Nimlgen** [[00:26:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1589)]
Oh.
Yeah.

##### **Geohot** [[00:26:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1589)]
See what I'm saying?
Like, is it the MEC?
Like, does the MEC have a cache?

##### **Nimlgen** [[00:26:42](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1589)]
Yeah, that's interesting.
But actually, I think it's.. Yeah, I mean, I had, like.. Like, yeah, I've seen that crashes.
And, I mean, the reason we see hang is sometimes we can see page faults because it just takes only the help of the address.
And the other help is zero, so I think it's, like, not filled with data.
It's not really.. I mean, it's GPU doesn't see this data.
Because sometimes we see somehow it's completely zero.
Yeah, I think I can also.. Okay, so yeah, I'll focus on this.

##### **Chenyu** [[00:27:40](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1660)]
OK, sounds good.
So I'm running out of tricks to make BERT faster.
The most immediate one I can see is random should be in one kernel.
And now it's three.
It's three because it has an Arange to start.
And there was a trick to cut the random into two parts, then combine them together.
And there, the cat generates one more kernel.
I would like to make one kernel, because RAND should be one kernel.
That requires FUSE ARAND.
FUSE ARAND sometimes in other places has other issues.
I don't know.
But it should work with RAND.
Yeah, but after that, I don't have other.
The BERTs looks.
pretty lean right now.
It's just things are not fast.
Even the forward is not fast.
So forward is about 350, 300 to 350.
So that's like 30-something percent utilization.
And inference doesn't use random.

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Why is it slow?
Is it the gemm that's slow?

##### **Chenyu** [[00:29:11](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
I think gemm is slow.
So our gemm is only, in our benchmark, the gemm is only fast if it's really, really big.

##### **Geohot** [[00:29:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Do you want to post the size of the gemm?
And I can just look into that.

##### **Chenyu** [[00:29:25](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Sure.

##### **Geohot** [[00:29:26](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Yeah, if we could get some micro benchmarks, maybe.
Get some micro benchmarks.
You're like, you make this faster, and Bert will get this much faster.

##### **Chenyu** [[00:29:39](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
I could take a look at that.
Yeah, I was doing that by stripping out components to the layers so that it's only gemm that's left.
I can post the size, or I'll have a script that kind of replicates this.

##### **Geohot** [[00:29:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Yeah, and I wonder, how bad is this gemm?
How many teraflops for GPO?

##### **Chenyu** [[00:30:00](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
We have multiple, so I need to take a look.
We have multiple with different size.
Yeah, so I'll probably be focusing on RAND 1 kernel.
And I'll see what's the issue with fuse Arange.
It sometimes works, sometimes fails.

##### **Geohot** [[00:30:18](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Yeah, we probably just need to expand that pattern a bit, if we could do that.

##### **Chenyu** [[00:30:23](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Yeah, I think I'm not too sure about the current way it's done.
So the current way is too loose, I think, because it will fuse too many stuff still.
But I'm not too sure.
Anyway, we're looking to see.

##### **Geohot** [[00:30:39](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
We could also potentially put reduce back in.
I don't know if this helps at all, but right now we're doing the thing with define ACC and assign and stuff.
We could potentially do graph rewrites while it's still a reduce op.
I don't know if that helps.

##### **Chenyu** [[00:31:00](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
I'm not following.
Which is this?

##### **Geohot** [[00:31:04](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
So we do in lower, we rewrite the reduce access.
to a define ACC add and assign, we could potentially bring back the reduce op, which is just like a reduce access op.
And then that might be easier to see the Arange pattern.
I don't know if that actually helps.

##### **Chenyu** [[00:31:28](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Interesting.
Now it fails at higher level.
Now it fails at scheduling.

##### **Geohot** [[00:31:33](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Oh, it fails at scheduling.
Oh, that's OK.

##### **Chenyu** [[00:31:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Yeah, so there's that.
Oh, speaking of reduce axis, do we want to match the Torch behavior that empty string is everything?
That feels weird, and it's not documented anywhere.

##### **Geohot** [[00:31:48](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
I agree that it's weird, and I wasn't thrilled about the hacks to do that.
I don't know.
No, I don't think it's right.
I don't think we should match that behavior.
If it's not documented, I don't think we should.
We'll just do it now in Torch.

##### **Chenyu** [[00:32:02](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
I was checking some documents, and it only says it's reduced over the dimensions if it's a tuple.
So by that definition, empty should be nothing.
That's what we are doing now.
I think this is quite obvious, because the output shape would be different.
So I don't worry too much if people use this wrong.

##### **Geohot** [[00:32:28](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
Yeah, I mean, we should just hack it in the Torch front end and say this is just to match Torch's behavior.

##### **Chenyu** [[00:32:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1747)]
OK, great.
Speaking of this, we want to support the low level shift stuff.
So we want to shift stuff in the tensor level, like tensor left shift another tensor, and things like that.
And I saw your todo.
Do we want to support this assuming the support on device?

##### **Geohot** [[00:33:02](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1982)]
Yeah.
I mean, you can also just use pow for that.

##### **Chenyu** [[00:33:10](https://www.youtube.com/watch?v=hIWzGyEX2do&t=1999)]
You can just pow.
I don't have a clean pow for that now.
I mean, the multiple, like multiply to the thing?
Yeah.
There you need to do the big cast, then big cast it back.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2016)]
Yeah, I don't know.
We should just support it.
I'm fine with adding it to the back ends.
We should support shift and do a rewrite if it can't do it.
I don't know.

##### **Chenyu** [[00:33:51](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2031)]
Maybe big cast is fine.

##### **Geohot** [[00:33:56](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2031)]
Yeah, I mean, the important thing that we have to do is we have to just get tensor working with shifts.
We should be able to shift tensors and stuff.

##### **Chenyu** [[00:34:07](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2031)]
OK, that's something I can do, or I can find something to do.
Cool.
OK, let's move on to schedule.

##### **Qazalin** [[00:34:15](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2055)]
Right.
Last week I merged cast-before-view.
So I think that got some speedups.
We also have fast-viz now.
So you can actually like viz the beautiful MNIST and BERT.
Hopefully that'll help us figure out where the gains are going to be.
I'm still, so I merged something that would get the kernels down for BERT, but it actually made step-time slower.
how would we do the benchmarking on these?
Because right now, I think we have enough infrastructure to mess with these expands.
But we don't actually know which ones are high leverage and valuable.
Do we need a memory profiler that could work on that?

##### **Geohot** [[00:35:11](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2111)]
Oh, yeah.
I think the memory profiler would be a good idea if you want to get a frame graph up for memory.

##### **Qazalin** [[00:35:19](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2119)]
I think we have to, like, do we understand why some expands are slower if we fuse them?

##### **Chenyu** [[00:35:30](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2130)]
So one major case is, I think it's because a safe pad thing, so some tensor core would be disabled.
So things that were previously triggered tensor core no longer triggers tensor core.
That's one.
For other cases, I don't know.

##### **Geohot** [[00:35:58](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2158)]
Oh, if we like put the expand and we're doing the math before the tensor core, maybe it doesn't trigger the tensor core.

##### **Chenyu** [[00:36:03](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2158)]
Yeah, that's one common issue why certain kernel becomes slower or certain parts of kernel becomes slower.
I think that we still have more infrastructural stuff to do before we, like, yeah, like I think the memory frame profiling is a good idea.
Also, how has becomes map coming?

##### **Qazalin** [[00:36:28](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2188)]
I'm gonna work on just refactoring the entire grouping part.
So yeah, it's in progress.
This week.

##### **Geohot** [[00:36:42](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2202)]
Cool.

##### **Qazalin** [[00:36:43](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2203)]
Yeah.

##### **Geohot** [[00:36:47](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2207)]
I mean, I clicked the profile button on on on viz.
And I think, in particular, this is something I'd really like to do in person, is think about what the unified Viz is going to look like.
So right now, Viz is visualizing the compilation, but it's not visualizing the runtime.
I guess the memory is kind of part of the compilation.
So we should think about how we want to visualize the memory in that graph.
Like the memory is determined by the, I was thinking about it.
You really can see it on the beautiful mnist.
Like your memory is determined by all your long edges and you could imagine like sliding across the thing and like drawing a line down the graph and everything that that intersects is using memory.
But yeah, I think, I think, so I think, I think like we still need more,
more visualization stuff and more scheduler refactors before we can really start fully talking about the assign.
Is multi-output kernels back?

##### **Qazalin** [[00:38:03](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2283)]
It requires first refactoring the grouper.

##### **Geohot** [[00:38:07](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2287)]
OK, cool.
Yeah, grouper refactor becomes map.
Nice to have cast before view back.

##### **Chenyu** [[00:38:19](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2299)]
Oh, yeah.
And nice job isolating why GPT-2 becomes slower.

##### **Geohot** [[00:38:27](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2299)]
Oh, what was it?

##### **Qazalin** [[00:38:28](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2308)]
It was wasting time doing reshapes.
Like, it's so good we have process replay on the scheduler.
So it goes from tensors from the big sync to the scheduled item ASTs.
So you could actually see the diff if it was doing three shapes, and it shouldn't do that.

##### **Geohot** [[00:38:51](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2331)]
Cool.
OK.
Becomes map and multi-output rollover.
And view is gone from the kernel graph?

##### **Qazalin** [[00:39:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2345)]
That also requires, again, doing that.
I was thinking about actually subbuffer
Subbuffer is just supported on some devices.
Like the offset function on the buffer is not supported.
Do we want a callback in those cases?
Because what I want to do really is in the schedule item buffers, I want to put the subbuffer instead of the actual base buffer for a set item.

##### **Geohot** [[00:39:34](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2374)]
Which devices don't support it?

##### **Qazalin** [[00:39:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2377)]
I think GPU hangs.
It was like offset function doesn't.

##### **Geohot** [[00:39:42](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2382)]
I think there's a way to do it.
I think maybe we should just add support to it and require it in the back end.
Yeah, it's called clCreateSubBuffer.
Probably should add support for it.
OK.

##### **Qazalin** [[00:40:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2405)]
I think that was the only bugger.
on the JIT side, but other than that, it's mostly the scheduler refactors.

##### **Geohot** [[00:40:16](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2416)]
Cool.
But we still don't have most of the views, right?
Or are all the views still there?

##### **Qazalin** [[00:40:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2429)]
The views are still there.
It's an all or nothing thing.
I can't do partially remove things.

##### **Geohot** [[00:40:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2437)]
Yeah.
Right now, I don't know like what what what is the current behavior if we don't support subbuffer?

##### **Qazalin** [[00:41:03](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2463)]
Like there has to be some way that's.
a set item is expressed in the kernel graph.
Because the buffer size is smaller than the kernel size, right?

##### **Geohot** [[00:41:19](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2479)]
You could always, like, you could always merge the subbuffer in, right?
So also,
Actually, let's be precise here.
What is supported on every device is a smaller size.
It just doesn't always support an offset.
Does that solve the problem?
Because you can always just imagine it's smaller.
There's no device where if I pass on a buffer that's size 200 and it only accesses the first 100, that that's going to do anything bad.
It just needs the offset.
But the offset's what you need to function for.

##### **Qazalin** [[00:42:01](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2521)]
Yeah, but you need the offset if your ShapeTracker is an offset, right?

##### **Geohot** [[00:42:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2525)]
No, you can always put that offset in the kernel, right?
I'm not exactly sure why you even need sub-buffers.
I understand why there's some.

##### **Qazalin** [[00:42:22](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2542)]
I want to literally take the kernel sources and materialize those buffers in the schedule item.
I want the kernel sources to be the correct representation of the buffers that are in the schedule.

##### **Geohot** [[00:42:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2557)]
I think the first thing to do here is to write some tests for the current sub-buffer behavior and make sure we understand all the different cases that can trigger it.
I know sometimes we were using sub-buffers to replace bitcasts, because you can also replace a bitcast with it.

##### **Qazalin** [[00:42:52](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2557)]
Yeah, we do that for disk.

##### **Geohot** [[00:42:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2557)]
But yeah, I think we should document the behavior of the current sub-buffer first.
Because I don't really like the idea of having to add it to OpenCL, because I always want backends that don't support it to just not support it, even if we could.
Yeah, but I don't feel that this is necessary.
I don't feel that supporting subbuffer is necessary to remove view from the kernel graph.

##### **Qazalin** [[00:43:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2597)]
It's not.
Yeah.

##### **Chenyu** [[00:43:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2601)]
Let's figure out how to do it with it.
Let's figure out how to do it without that.
But again, becomesMap and multiOutput

##### **Chenyu** [[00:43:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2617)]
Okay, let's move on.
Nimlgen

##### **Nimlgen** [[00:43:45](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2625)]
Yeah, so.. Yeah, so I'm going to look into the AM.
So this problem I want to talk about also is the main piece.
Yeah, for AM.
it is.
to help people with AMD for some reason.

##### **Geohot** [[00:44:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2625)]
Oh, is this why the ring is slow?

##### **Nimlgen** [[00:44:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2625)]
Yeah.
Yeah, it switches like seven gigabyte a second while AMD is supporting it.

##### **Geohot** [[00:44:16](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2656)]
Yeah, do you know why?

##### **Nimlgen** [[00:44:20](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2665)]
No, not yet.

##### **Geohot** [[00:44:23](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2665)]
Cool.
That's a good thing to look into.
Why is our disc only getting 10?
Why can't we get 20?

##### **Nimlgen** [[00:44:33](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2665)]
Yeah, I haven't looked into that yet.
But yeah, I've run it, and it's about 11, 12 discs.
I think we can get 20, yeah.

##### **Geohot** [[00:44:50](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2700)]
With DD, I can get 20.

##### **Nimlgen** [[00:45:00](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2700)]
Yeah, okay, I need to look into that.

##### **Geohot** [[00:45:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2700)]
Is there any DMA directly from the NVMe drives?

##### **Nimlgen** [[00:45:14](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2700)]
Yeah, like, in theory, yeah, of course.
But yeah, I'm not sure there is some API for this or like for the IOU, because it
I need to double check.
I think, yeah, definitely.
Like, in theory, I can do this, yeah.

##### **Geohot** [[00:45:36](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2717)]
Yeah, like, I'm even just saying, like, in IOU ring, what if you literally give IOU ring a GPU address?
Does that work?

##### **Nimlgen** [[00:45:47](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2747)]
So I think, yeah, if I give a mapped address to the PCI bar, I think, yeah.

##### **Geohot** [[00:45:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2755)]
Like, that'd be sick.
If you could just, yeah, tell the, like, don't even go through system memory.
Just literally tell the guy, oh, you ran to split it to the GPU.

##### **Nimlgen** [[00:46:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2765)]
Yeah, I need to play with it.

##### **Geohot** [[00:46:09](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2769)]
Cool.
Yeah, no.
First priority is bugs and fuzzing.
Fast ring reduce and fast drive load.
What I'm going to do after that drive load benchmarks fast, I'm going to run the, I'll run the PyTorch loader on the GPU.
So instead of loading LLaMA, like we're doing right now, and we load one weight at a time, that's always going to be slow.
Just copy the whole PTH file to the GPU.
Oh no, we wasted a few megs for offsets.
Who cares?
And then do the load and split them all into sub-tensors on the GPU.
That should let us load things so fast.

##### **Nimlgen** [[00:46:52](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2812)]
Yeah.

##### **Geohot** [[00:46:56](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2812)]
But yeah, cool.
Sounds like a good priority list.

##### **Chenyu** [[00:47:01](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2821)]
How did you fix the tiny 19 issue?
Because it's 5 GPU again.
I'm not sure if it's really fixed.

##### **Nimlgen** [[00:47:15](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2821)]
So no, I just did reboot.

##### **Chenyu** [[00:47:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2821)]
Yeah, so that's also what I did.
Then initially, it would show 6 GPU.
But once I started to run BERT,
it hands, and I check again, it becomes 5 GPU.

##### **Nimlgen** [[00:47:15](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2821)]
Yeah, I mean, well, I've collected the logs, and actually, like, the GPU simply, like, there is some information in the mask that GPU just pulled from the bus.
And it's just all these cases are just the same GPU.
So I'm just doing a run right now, monitoring temperatures.
So maybe that's the reason.
I don't know.
Yeah, but so far it's good.

##### **Chenyu** [[00:48:04](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2884)]
OK.
Now we have 10 minutes left.
Let's give a quick update on some of the ongoing bounties or works.
Let's start with tinychat.

##### **Hooved** [[00:48:19](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2899)]
Hey.
Yeah, so I did everything I wanted to do.
The PRs have been ready for review for TinyChat for a few days now.
I saw Chenyu merge the first one.
Thank you.
And then there's the remaining two parts for the TinyChat boundary.
The remaining two PRs that are awaiting review are covering how we compile and export the TinyChat model in a way that's suitable for the browser.
And then the final PR is the browser app.
So just waiting for feedback on that.

##### **Chenyu** [[00:49:03](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2943)]
Sure.
First, do you want to review or take a look

##### **Geohot** [[00:49:08](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2943)]
Yeah, I can do this.

##### **Chenyu** [[00:49:09](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2943)]
I think it's fine mostly, but I just don't know too much about Wasm.

##### **Geohot** [[00:49:16](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2943)]
Yeah, I can review this tomorrow.
It looks pretty good.

##### **Chenyu** [[00:49:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2943)]
There's an instruction for to run the script to reproduce the code.

##### **Geohot** [[00:49:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2943)]
Yeah, I think that the code itself looks good.
I think it's 10:50 PM here.
But yeah, tomorrow morning I will try this on my machine.
And yeah, I think if things look good, as long as it works on my machine, I think we should be good to merge these and give you the bounty.
These are really high quality PRs, by the way.
Thank you.

##### **Hooved** [[00:49:53](https://www.youtube.com/watch?v=hIWzGyEX2do&t=2993)]
Thanks.
I appreciate it.
And I look forward, if there's any problems, ping me, at me, and I'll help you troubleshoot them.
Thanks.

##### **Geohot** [[00:50:01](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3001)]
Cool.

##### **Chenyu** [[00:50:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3006)]
That's good.
Yeah, so I think after that, we want to improve the export thing.

##### **Geohot** [[00:50:15](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3006)]
Yeah, I mean, export should really go into main TinyGrad.

##### **Chenyu** [[00:50:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3006)]
Yeah.
I think export and Onnx are the two next things we want to merge into the main TinyGrad tree.

##### **Geohot** [[00:50:28](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3006)]
Yeah.
I mean, just to be able to do straight up ONNX to export model.
like ONNX to WebGPU, which is like a flow in MainTinyGuard would be great.

##### **Chenyu** [[00:50:47](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3047)]
ONNX, I saw the thing in channel.
I think few separate things.
CI should ideally be future proof.
So we don't want any dynamic things that determine the size or the model you're running for CI, because that will break someday.
In principle, having a script that runs a fixed set of models and making sure it works.
Making sure all the ONNX ops are supported, I think, is good enough for less specific bounty.
I think we should be close to getting a merge.
And for now, if the only left issue is something is not supported, I see like zeroing it off some of the list.
We, we don't have a good way to support anyway.
So having the script, having that ready, then we can think about how to move more stuff from electronics to, to maintaining grad.

##### **Geohot** [[00:51:53](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3047)]
Yeah.
I posted in tinygrid dev, but I think the, uh, the API should look like
We'll create a new folder called FrontEnd.
Overall, I think the ONNX code is pretty high quality.
So we can raise the line limit as appropriate for that.
And just like, yeah, timing quality of life refactors.
It's OK if it imports from ONNX, but it shouldn't import from NumPy.
And it also shouldn't take in an ONNX model object.
It should just take in a path or a URL.
So that's done.

##### **Chenyu** [[00:52:23](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3143)]
How do you want to parse proto?

##### **Geohot** [[00:52:30](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3150)]
Oh, we can just import ONNX.
That's fine.

##### **Chenyu** [[00:52:33](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3153)]
Oh, OK.

##### **Geohot** [[00:52:34](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3154)]
Yeah, I mean, the ONNX front end needs ONNX, and the PyTorch front end needs PyTorch.
Like, you know, whatever.

##### **Chenyu** [[00:52:43](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3163)]
Cool.
OK.

##### **Chenyu** [[00:52:44](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3164)]
Now let me know if there's anything you need me to review for ONNX.
Let's push this a little bit so we can have the scripts and decide how to really move stuff into TinyGrad.
Next, we have AMX Tensor Core.

##### **Ignaciosica** [[00:53:04](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3184)]
Hi.
Hello.
I posted a question on the channel.
I just started the refactor.
I couldn't work much last week.
But I'm not sure about the refactor you specified, George, where you talked about.

##### **Geohot** [[00:53:23](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3203)]
Well, no, but you load from the regs.
The UOp is load, right?
The same way the UOp is load from Define Global?

##### **Ignaciosica** [[00:53:34](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3214)]
Yes.

##### **Geohot** [[00:53:36](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3216)]
Maybe the first thing, like you can think about how it would work right now for ACC.
Like right now, we just put the define ACC directly into like an add or something.
But you could imagine a load going there, right?
You could imagine it be define ACC, load, and then the add.
And there has to be a load there to load it off of the define.
And then the assign becomes store.

##### **Ignaciosica** [[00:53:59](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3239)]
Yes, but I think load loads into something, no?

##### **Geohot** [[00:54:04](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3244)]
No, load doesn't load into anything, right?
Like load just means, so there's really multiple things here.
There's like, there's global buffers, local buffers, registers, which are things like accumulators.
And then there's just the implicit thing, right?
So there's not going to be a load in store between like, say I have like a multiply followed by an add.
There's not going to be a load in store there.
That's an implicit register.
But whenever you have an explicit register, it's fine to have to load from it, like a defined ACC.

##### **Ignaciosica** [[00:54:32](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3272)]
Okay.
Yes.

##### **Geohot** [[00:54:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3275)]
Yeah, play with it a bit.
I really think a load does make sense.

##### **Ignaciosica** [[00:54:40](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3280)]
OK, sure.

##### **Geohot** [[00:54:40](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3280)]
Even if that load ends up being a no-op in C style.

##### **Ignaciosica** [[00:54:46](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3286)]
Yes.
OK.
Thank you.

##### **Chenyu** [[00:54:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3286)]
OK.
RetinaNet?

##### **Flata** [[00:55:02](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3302)]
So.
Yeah, so the training, I've already started a couple of them.
I think I'm not trying to get the time down just yet, focusing on the correctness run.
I think we're pretty much aiming towards the target metric.
I think I just checked the latest one that I ran.
It's just like 0.001, I think.
It's really close, but it looks like it needed another epoch from four to five.
So I'll see if I can hyper-parameter tune that just to see if it can get under the..
before Epoch run.
So that's what I'm kind of working on.
But I think the two bottlenecks right now are the eval, for sure, because it takes, I think, like an hour and a half maybe to just go through, I think it's like 20k, probably like 25k images for the eval, and then try to see if I can optimize more on the forward time as well.

##### **Chenyu** [[00:55:52](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3352)]
Yeah, so I'm reading your run.
So this is 6 GPU, right?

##### **Flata** [[00:55:58](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3352)]
Yes, that's right.

##### **Chenyu** [[00:55:59](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3352)]
And it's only 77 t-flops, so not very impressive.

##### **Flata** [[00:56:05](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3365)]
Yeah, it definitely needs to go up.

##### **Chenyu** [[00:56:09](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3369)]
OK.
And this one, this 20, 30 hours, so I see the most recent round took 30 hours to finish.
And you say the eval is pretty close.
It might just be noise.
But say if this run is within 24 hours, is it finished?

##### **Flata** [[00:56:33](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3393)]
No, not quite.
I think by the time it hits a 24-hour mark, I think it's probably evaluating after the third epoch, I think.
That's what I've been tracking.

##### **Chenyu** [[00:56:41](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3401)]
Yeah, my point is that everything else seems correct to you, and it's just the timing and the speed is the only issue.

##### **Flata** [[00:56:52](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3412)]
Yeah, I think so.
I'm pretty confident with the metric itself, reaching towards that.
So I think it's just really the timing and speed.

##### **Chenyu** [[00:57:02](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3422)]
So I think one first thing I would try is, first, I see you have many BEAM parameters.
Just remove those all out.
I think those are smaller than default.
And you want to see the potential of this.
So I would start with removing those.
I'll use the default to see if it's faster.
Maybe it's already faster with that.

##### **Flata** [[00:57:26](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3422)]
OK, sounds good.

##### **Chenyu** [[00:57:32](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3452)]
Cool.
And obviously, if we want to submit MLPerf, we need to be much faster.
But a good run.
So the target metric is 0.34?

##### **Flata** [[00:57:45](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3422)]
Yes, that's right.

##### **Chenyu** [[00:57:48](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3468)]
OK.
Sounds good.
We can coordinate in the TinyBox access panel.
Because we only have three green box, and everyone wants to use their green box.

##### **Flata** [[00:58:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3486)]
OK, sounds good.
I'll probably stay on Tiny14 for probably, I don't know, maybe the next 30 hours, one more time.
And then I think I can give that up.
Someone else can use it.

##### **Geohot** [[00:58:16](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3496)]
Is there a reason you can't use a red box?

##### **Flata** [[00:58:20](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3500)]
So the, it is slower and also the AM, I think I posted it in the, uh, I'm over for it's in a net channel.
The loss, if I use the AM driver specifically, it's like very, like very odd values for things like very large and negative values that I'm getting.
So there was also that as a blocker.

##### **Geohot** [[00:58:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3517)]
Oh, we got a, okay.
If there's some bug in the AM driver, again, we really got to fix that.

##### **Chenyu** [[00:58:44](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3517)]
But can you run with AMD backend.

##### **Flata** [[00:58:49](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3529)]
I can, I can actually.
Yeah, it is slower.
So AMD is good.
It's just AM that's causing that weird loss value.

##### **Chenyu** [[00:58:56](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3536)]
So while you are waiting, try to also improve or run something on AM.
I know it's probably taking longer, but eventually we want this to work on both green box and red box anyway.
And we have a lot more red box that's idle resource.

##### **Geohot** [[00:59:12](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3536)]
Yeah, the red boxes are free.
I got six more of them, too.
So there's more red boxes if you want more red boxes.
No, but if there's some driver bug, yeah.
If there's any way you can root cause that, that would be great, too.
Like find one kernel that's failing or something.

##### **Chenyu** [[00:59:40](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3536)]
Yeah, no, that's slightly annoying, because I also had that issue.
And I'm pretty sure it's not kernel that's failing.
It feels more like the data is not synced properly, or something is not copied right properly.
Yeah, there are some slight methods.
Yeah, I also have that, but sometimes I retry and it works.

##### **Geohot** [[01:00:14](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3614)]
Yeah, we got to fix this.
Yes.

##### **Chenyu** [[01:00:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3621)]
OK.
Let's quickly talk about the remove compiler stuff for AMD.

##### **B1tg** [[01:00:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3629)]
Hi, I was doing the LLVM backend bounty recently and now we can use the upstream LLVM like LLVM18 and LLVM19 to directly compare LLVM IR to the AMD GPU targeter.
Now the implementation basically works on TinyBox Red, and the Remu caused some test failure.

##### **Geohot** [[01:01:00](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3660)]
So how sure are you that these are Remu?
Because I just read what you wrote, and what you're running on macOS is not a real AMD GPU.
They're both Remu.

##### **B1tg** [[01:01:14](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3674)]
Yes, the test on the Mac is only the test_ops.
Yeah.
And there are other tests on the Linux backend.

##### **Geohot** [[01:01:34](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3674)]
So if it's a Remu bug, do you know what the Remu bug is?

##### **B1tg** [[01:01:37](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3674)]
Oh, the error shows remutant support new instruction introduced in this kernel.

##### **Geohot** [[01:01:49](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3709)]
Oh, can you just post what the instruction is?
Qazalin, can you fix this?

##### **B1tg** [[01:01:58](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3718)]
Oh, I will post it in the PR.

##### **Geohot** [[01:02:06](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3726)]
Great.
Yeah, we'll get that fixed.
I'm sorry.
Once things go to the second page of PRs, I need to be better at just clicking at it and looking at them.
But yeah, OK.
So you think it's good, but it's just Remu bugs.
Why is it taking 14 minutes?
Again, it's just the bugs?

##### **B1tg** [[01:02:31](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3751)]
You mean the speed is too low?

##### **Geohot** [[01:02:35](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3755)]
Well, yeah, I see that test taking a ton of time.

##### **B1tg** [[01:02:43](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3763)]
Because we didn't implement the local in the LLVM backend.

##### **Geohot** [[01:02:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3775)]
Wait, what do you mean?

##### **B1tg** [[01:03:00](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3780)]
I mean, the local support are not implemented in the LLVM render.

##### **Geohot** [[01:03:11](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3791)]
Oh.
Oh, that should be easy to add, right?

##### **Geohot** [[01:03:29](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3809)]
So wait, but I said, do you mean like, why is that not, so you're saying there's no locals?
I mean, it's, the thing is, it's not really like LLVM.
It's really AMD.
Interesting.
Cool.
I will, I will, I'll play with this a bit tomorrow.
Okay.
And I see you said has local equals true.
That doesn't work?

##### **B1tg** [[01:04:09](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3849)]
No.
Some instruction or some code is not implemented yet.

##### **Geohot** [[01:04:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3857)]
In TinyGrad?

##### **B1tg** [[01:04:19](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3859)]
Yes, in the LLVM render code gen.

##### **Geohot** [[01:04:32](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3872)]
Why that?

##### **B1tg** [[01:04:38](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3878)]
I think it's because the LLVM IR was running for the CPU.
We don't support the multi-thread stuff.
So we lack the local support.
But for the GPU backend, we have the local support.
So now we want the LLVM IR to support both the CPU and the GPU.
So we need to bring the local support to it.

##### **Geohot** [[01:05:21](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3921)]
I see.
Yeah, no, I mean, we're definitely going to need to get locals working in order to merge this.
I'll look into this tomorrow.
I don't exactly understand why it doesn't work.
But I'll add this to my list tomorrow.
And I will post what REMU instruction is, and we'll get that fixed.

##### **B1tg** [[01:05:36](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3936)]
OK.

##### **Geohot** [[01:05:40](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3940)]
Cool.
Yeah, looks good.
We got that battery locked, so we'll make progress with this.
I'll give you feedback tomorrow.
OK.

##### **Chenyu** [[01:05:58](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3941)]
Sounds good.
Anything else?
Making good progress.
torch frontend is exciting.
So for the people in this meeting, try your favorite Torch script.
Try to run it onto any grab back end, and open issue if something doesn't work.
Or open issue if it's something that is not already covered by other things that is not working.
Let us know.

##### **Geohot** [[01:06:31](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3941)]
Uh, yeah, let me, let me try to explain this in like, in like really simple terms for people here.
So you know how like torch has different devices, right?
You know how you can do like in torch, you could do like dot CUDA or dot CPU or dot MPS on Apple.
So what the tinygrad backend is, is you copy and paste these three magical lines, which patches a new device into pytorch called tiny.
And then you can do dot tiny in the same way you do dot CUDA.
But the thing about dot tiny is it uses tinygrad.
So if you have like a GPU that only has OpenCL support, for example, if you have a GPU that's like just OpenCL, there used to be no way at all to use that with PyTorch.
But now you can use the tinygrad backend.
The tinygrad backend will take the PyTorch and compile it into OpenCL code, which will run through the tinygrad OpenCL backend on the GPU.
and then pass that back to Torch, you'll be able to run PyTorch programs with the TinyGrad backend everywhere TinyGrad supported, which includes some crazy targets like Qualcomm GPUs, Qualcomm DSPs, all these things.
But yeah, so hopefully everyone understands what it means when it's like actually go and try a PyTorch program with the TinyGrad backend.
The three lines are a little annoying.
It'd be nice when it's just one.
Actually, I think I'm going to do that.
I think I'm going to add that as a file.
I think I'll add TinyGrad frontend PyTorch and just make it import from extra.

##### **Chenyu** [[01:08:15](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3941)]
Then we cannot do a release with that?

##### **Geohot** [[01:08:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=3941)]
No, it won't be included in releases.
We won't put that folder in releases yet.
But yeah, no, I think just you have to install tinygrad not from a release.
You have to install tinygrad from source.
I'll have it assert and say that.
That's on my list for tomorrow, too.
I got a list for tomorrow.
Right on the whiteboard.
I got LLVM, I got tinychat, and I got frontend.torch.

##### **Chenyu** [[01:08:55](https://www.youtube.com/watch?v=hIWzGyEX2do&t=4135)]
Cool, sounds good.
OK, that concludes this meeting.
Thanks, everyone.
We have meetings every Monday around the same time.
Unless it's a different time, then we would let you know early.
And that's it for this meeting.
See you next week.

##### **Geohot** [[01:09:17](https://www.youtube.com/watch?v=hIWzGyEX2do&t=4135)]
Bye!
