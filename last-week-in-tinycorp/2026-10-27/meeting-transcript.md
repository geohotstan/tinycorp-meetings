# 2026-10-27 Meeting

### Meeting Agenda

**Time:** new meeting #43, 10/27 12pm Hong Kong time
Free-form meeting this week, no agenda.

### Audio

[Youtube Link](https://www.youtube.com/watch?v=jvlYYYAnRvM)

### Highlights

- **[GLM Self-Hosting Status](#wozeparrot-000033)**: GLM runs on tinygrad loaded from the Hugging Face FP8 checkpoint (GGUF has no FP8 type) at about 20 tok/s with TP8. It's still slow, but Geohot wants to support both lab-published weights and GGUFs.
- **[Beating SGLang](#geohot-000421)**: SGLang peaks around 220 tok/s once warmed up. Geohot wants to match its 1M-context support, with roughly 16 concurrent sequences and LRU caching. A simple policy would choose between prefill and decode.
- **[Paged Attention via the MMU](#geohot-000139)**: Geohot asks whether the MMU can handle KV cache paging, and Nimlgen says page changes should be easy. Later (00:25:43) Geohot decides it's premature, since GLM will fit plenty of KV caches.
- **[Switch-Over Deadline](#geohot-000928)**: Wozeparrot expects something fast by the end of next sprint and two sprints for a clean merge to master. Geohot wants the other two machines running the tinygrad server within three weeks, with SGLang shut down.
- **[GPU Reservation System](#chrism-001048)**: Chrism demos the SSH gateway (port 22222) for creating VMs like a 4090. Users jump through it as `runner@`, and instances must be deleted manually. Agents can use it too, but GLM needed hints about `-J` and the username.
- **[Network Isolation and DMZ](#chrism-001204)**: The gateway isn't publicly accessible yet, and a DMZ node modeled on Comma's setup is planned. Geohot wants tinygrad isolated from Comma's network, ideally with its own router.
- **[Kimi on the SSD Machine](#nimlgen-002125)**: Nimlgen is at about 25 tok/s on the SSD-backed machine, up from 14 to 18 just from the new GPUs, with the rest coming from speculation. He's aiming for a stable 30, which Geohot calls potentially a sellable box and the ultimate HCQ2 stress test. Upstreaming starts with the NVMe device and HCQ cleanup.
- **[Assembly Emulator and Linking](#qazalin-002614)**: Qazalin's CPU-only assembly emulator branch should merge by end of week, with each instruction as its own BINARY UOp linked at runtime. Geohot pushes him to reuse HCQ2's existing linker and `runtime_cache` instead of writing a second one.
- **[Line Count and Cleanup](#geohot-004203)**: tinygrad stands at 25,616 lines, with ops the worst offender. Geohot floats compiling the pattern matcher into one generator that yields every match. He also wants the `isa` folder deleted and x86 moved into renderer.
- **[studentgrad Progress](#geohot-004608)**: Geohot has an MNIST trainer, a Qwen runner and a ResNet runner working. Rules are relaxed gradually week by week, with symbolic and syntactic sugar in week six and GPUs not before week seven.
- **[AMD PSP Trust Break](#geohot-004710)**: Shout-out to Blasty for what looks like a full boot-time and runtime trust break of the AMD GPU's PSP. Geohot speculates about rooting it to enable resets, or making the GPUs PCIe hosts.
- **[Company Update](#geohot-005359)**: Big progress on the secret project, and a PO was sent this morning. Geohot says this is why the LLM stack has to work really well, since that's what people will buy these boxes for.
- **[llm.tinygrad.win](#wozeparrot-005426)**: Wozeparrot has a public endpoint up for GLM and GLM Flash behind a Cloudflare tunnel, with Kimi to be added. It uses a custom async router that does token routing, request normalization and request priority. Geohot plans one key for employees and one for Comma, and GLM Flash handled 64 concurrent requests with zero errors.

### Transcript
##### **Qazalin** [[00:00:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=0)]
We'll have a short meeting today. We don't have any agenda.

##### **Geohot** [[00:00:04](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=4)]
We'll have a meeting?

##### **Geohot** [[00:00:12](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=12)]
All right, well, we'll do this a little more free-form then, since there's no agenda. I think the main thing we want to talk about is: how close are we to self-hosting our LLMs?

##### **Wozeparrot** [[00:00:33](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=33)]
So I have GLM working. It's slow.

##### **Geohot** [[00:00:40](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=40)]
How slow? Why? I mean, it's GLM; we can just make it fast.

##### **Wozeparrot** [[00:00:44](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=44)]
Yes.

##### **Geohot** [[00:00:50](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=50)]
How much of that can we merge?

##### **Wozeparrot** [[00:00:58](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=58)]
The other thing is, I was working on GLM loaded from the Hugging Face checkpoint rather than the GGUF, so that we have FP8. GGUF doesn't have an FP8 data type.

##### **Geohot** [[00:01:14](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=74)]
Yeah, I think we should load from the safetensors, or whatever is on Hugging Face.

##### **Wozeparrot** [[00:01:22](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=82)]
So we load from that, and we get about 20 tokens a second right now.

##### **Geohot** [[00:01:32](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=92)]
We got to go a lot faster than that.

##### **Wozeparrot** [[00:01:34](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=94)]
Yeah. I just haven't pointed an agent at it and said, "Make it fast," yet.

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=99)]
We also have to think about how we want to manage KV caches. Do we want paged attention? Does anyone know why they don't just use the MMU for paged attention? How easy is this for us if we just want to use the MMU?

##### **Nimlgen** [[00:02:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=135)]
It should be easy to change pages on the MMU. I can look into that.

##### **Geohot** [[00:02:29](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=149)]
We have to deal with KV cache management, and we should have plenty of extra RAM running GLM. So that's 20 tokens per second. How's it sharded?

##### **Wozeparrot** [[00:02:43](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=163)]
TP8.

##### **Geohot** [[00:02:45](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=165)]
TP8, okay. TP8 is probably what we want.

##### **Wozeparrot** [[00:02:50](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=170)]
As far as I can tell, no one is doing EP single-node.

##### **Geohot** [[00:02:55](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=175)]
TP8 is fine, and we should be able to get the latencies to be quite low on the all-reduces. I have my branch, and it has a lot of good stuff in it. We just have to figure out how to get it out and get it merged. What's our current... We're getting like 150 tokens per second now on SGLang?

##### **Wozeparrot** [[00:03:26](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=206)]
I haven't measured recently, but...

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=240)]
All right. It's loading the whole... I'm looking at the Docker log now. This is from September. It looks like we're not even getting 100 tokens per second on most decodes, so this actually should be pretty easy to beat.

##### **Geohot** [[00:04:21](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=261)]
Oh, no. Okay, wait. It gets faster once it starts up. It will go up to 220. And then how many one-million-context KV caches can we fit?

##### **Wozeparrot** [[00:04:50](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=290)]
I haven't measured, but we should be able to fit at least as much as SGLang.

##### **Geohot** [[00:04:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=296)]
I wonder if we even have to go to...

##### **Wozeparrot** [[00:05:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=305)]
I never even get up to a million. I find that it breaks down quite a bit.

##### **Geohot** [[00:05:12](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=312)]
I want to support it.

##### **Wozeparrot** [[00:05:14](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=314)]
800K.

##### **Geohot** [[00:05:16](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=316)]
SGLang supports it, so I want to support it. I want to fit, I don't know, maybe we could support something like 16 concurrent, and then just LRU caching for now. Hopefully we can max out the FLOPS with just a single sequence. A single sequence does prefill, so decide a little policy to choose between prefill and decode.

##### **Geohot** [[00:05:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=351)]
What I've been doing against my branch, and what I want to do more thoroughly, is I want to run DeepSWE. I want to run Terminal-Bench. I want to run basically all the...

##### **Wozeparrot** [[00:06:06](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=366)]
Which Terminal-Bench are you running? I was looking into running Terminal-Bench, and the new one has a bunch of CUDA kernel stuff.

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=376)]
I just ran 2.1. That's what a lot of the published numbers are. Terminal-Bench 2.1.

##### **Geohot** [[00:06:37](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=397)]
Why doesn't my other microphone work? My other microphone is a lot better. This mic should work.

##### **Chrism** [[00:06:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=408)]
Mic seems fine.

##### **Geohot** [[00:06:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=411)]
Does this one work?

##### **Chrism** [[00:06:53](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=413)]
Oh, that one works.

##### **Geohot** [[00:06:54](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=414)]
Oh, great. That's the better one. I don't know what the problem is. Maybe I clicked on the wrong thing. Great. So what's our ETA look like on switching GLM?

##### **Wozeparrot** [[00:07:17](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=437)]
Let's see. I want to have something by the end of next sprint.

##### **Geohot** [[00:07:28](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=448)]
End of next sprint? You think it'll be really solid?

##### **Wozeparrot** [[00:07:31](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=451)]
I don't think it'll be really solid. I think we'll have something fast by the end of next sprint, but it won't be very clean.

##### **Geohot** [[00:07:37](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=457)]
Okay. But in master?

##### **Wozeparrot** [[00:07:42](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=462)]
In master, I would give it two sprints.

##### **Geohot** [[00:07:46](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=466)]
I already have this for GLM Flash. It works pretty well. That branch works pretty... It's really easy, and we need to just be putting the LLMs on this stuff, because it does just work. But then we have to figure out how to constrain...

##### **Wozeparrot** [[00:08:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=480)]
I was looking through your branch, and some of the code was...

##### **Geohot** [[00:08:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=485)]
The code's kind of crappy, but I didn't tell it to make the code better. I told it to make it work.

##### **Geohot** [[00:08:13](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=493)]
We got to get switched over to this. We got to think about it from the perspective of running these aggressive benchmarks against it and all of that being fast. Figure out what concurrency we can fit. Okay, so end of next sprint, let's be converted over. And you think that's just GLM, or once we get one, it'll be easy to do the other?

##### **Wozeparrot** [[00:08:44](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=524)]
Depends on how Kimi is run. I think the way B1TG was doing Kimi was through the GGUF quant, which I don't know if we want to do it that way. I feel like it's better to load the native way.

##### **Geohot** [[00:09:03](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=543)]
Is this loading thing really that annoying?

##### **Wozeparrot** [[00:09:07](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=547)]
For weights?

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=549)]
Yeah.

##### **Wozeparrot** [[00:09:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=551)]
No. Once we have one in, the other one should be fairly easy.

##### **Geohot** [[00:09:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=555)]
I think we should support loading from both whatever the way they're published by the labs is and the GGUFs.

##### **Wozeparrot** [[00:09:26](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=566)]
Yeah. It's just loading from the checkpoint.

##### **Geohot** [[00:09:28](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=568)]
I don't think that's going to change any of that. All right, cool. In three weeks, I want to be switched over to our server on the other two machines and shut SGLang down.

##### **Geohot** [[00:09:44](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=584)]
Then we can use the remaining servers to run the same thing, but run aggressive benchmarks against it and improve the thing. I have this stood up already on tiny-s1 and tiny-s2. Tiny-s1 is my playground server, where I work to improve GLM Flash. Tiny-s2 is running GLM Flash. Has anyone here used it?

##### **Wozeparrot** [[00:10:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=615)]
Not yet.

##### **Geohot** [[00:10:17](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=617)]
I don't know if anyone's going to use it. It's GLM Flash, but it does work. It needs more work to support multiple users, but it works. Prefill and decode are very fast. I want speeds that are higher than SGLang. There's no reason we can't.

##### **Geohot** [[00:10:41](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=641)]
Can I reserve a 3080?

##### **Chrism** [[00:10:44](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=644)]
You can.

##### **Geohot** [[00:10:45](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=645)]
How do I do it?

##### **Chrism** [[00:10:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=648)]
You SSH to TGW2 on port 22222. That's five twos. It has a little interface like the way that git add -i looks. But you can also put a command straight on SSH, as if you were typing a command to run. You can do "create" and then the VM type, and it will create it.

##### **Chrism** [[00:11:22](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=682)]
Probably don't reserve the 3080, because I think we use those more frequently. Actually, maybe it's fine. You can reserve the 3080. It's probably fine. Although for testing, I've been doing the 4090s. Is that working?

##### **Geohot** [[00:11:44](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=704)]
No. What's the port of that gateway?

##### **Chrism** [[00:11:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=711)]
The port is five twos.

##### **Geohot** [[00:11:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=716)]
Wait, so I actually have to tunnel through the ProxyJump to get to this?

##### **Chrism** [[00:12:04](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=724)]
Yes. It is not publicly accessible yet. I talked to Comma about getting that to be publicly accessible, and we will get that to happen. But Harald is very concerned about having stuff public-facing to the internet, so we'll probably have gateway three be...

##### **Wozeparrot** [[00:12:24](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=744)]
That's why I was asking if we wanted to preload, because if we aren't preloading, then I can free up gateway three as our DMZ node.

##### **Geohot** [[00:12:33](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=753)]
We don't need to preload weights anymore.

##### **Chrism** [[00:12:35](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=755)]
The idea is that gateway three would be a DMZ that's only connected to... I guess that can't quite be true. Harald was saying we should set it up similar to the way that Comma has our DMZ stuff set up. I'll have to understand exactly how that works.

##### **Geohot** [[00:13:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=780)]
I just want to be able to put things on ports. I don't know exactly what the configuration is going to be, but get tinygrad... Let's just make sure it's all pretty isolated.

##### **Chrism** [[00:13:10](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=790)]
I agree.

##### **Geohot** [[00:13:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=795)]
We shouldn't be on Comma's network anyway.

##### **Chrism** [[00:13:17](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=797)]
We're still behind the router.

##### **Geohot** [[00:13:22](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=802)]
Yeah, but still, we should be aggressive.

##### **Chrism** [[00:13:26](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=806)]
It would be quite nice if we were no longer behind the router. Obviously in some way we need to be behind the router, but if they could set it up so we can manage everything... Every time I ask them to make a change in the router, they're always very scared they're going to take something offline for their infrastructure.

##### **Geohot** [[00:13:40](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=820)]
I very much like this. Let's see what we can do. I'd like to run our own router. I need an invite code.

##### **Chrism** [[00:13:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=831)]
Wait, are you not using your SSH key?

##### **Geohot** [[00:14:03](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=843)]
Are you using my GitHub SSH key?

##### **Chrism** [[00:14:06](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=846)]
It's whatever's in infra.

##### **Geohot** [[00:14:08](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=848)]
If it's what's in infra, then... Oh, maybe I have the wrong user. Hang on.

##### **Chrism** [[00:14:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=855)]
The username also matters. There's also a way to set up invite codes. I'll write something up about how that works.

##### **Geohot** [[00:14:26](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=866)]
All right. Create. I'll create a 4090. That's pretty nice. Are we going to include the price, how much I'm getting billed?

##### **Chrism** [[00:14:40](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=880)]
Yeah.

##### **Geohot** [[00:14:43](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=883)]
Creating instance. Are there races here? What happens if I exit out of this?

##### **Chrism** [[00:14:49](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=889)]
If you exit out of it, you won't get to see that the instance was created, but it'll create.

##### **Geohot** [[00:14:53](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=893)]
Okay, great. I have an instance.

##### **Chrism** [[00:14:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=896)]
Now you jump through this server, where the destination hostname is the name of the instance you created, which is probably going to be a little annoying if you didn't configure this in your SSH config.

##### **Geohot** [[00:15:12](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=912)]
No, I did. I called it "reserve" in my SSH config.

##### **Chrism** [[00:15:19](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=919)]
So, -J reserve, and then the...

##### **Geohot** [[00:15:20](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=920)]
-J reserve. Okay, I need a password.

##### **Chrism** [[00:15:25](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=925)]
Sorry, it's runner@. You have to do runner@. I should fix that.

##### **Geohot** [[00:15:29](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=929)]
Not only that, password auth. Why is password auth enabled? But I guess this is through so many layers of security. Oh, sweet. I'm in. Do I have a GPU? sudo modprobe nvidia. Didn't work.

##### **Geohot** [[00:15:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=951)]
Oh, it did. There was just lag. What?

##### **Chrism** [[00:15:58](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=958)]
Weird. It's probably, if you're from Hong Kong, it's going to be a little slow, right?

##### **Geohot** [[00:16:03](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=963)]
No, not Hong Kong lag. Look at what I posted. I don't know why modprobe returns and the GPU is not enumerated, but it's fine.

##### **Chrism** [[00:16:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=975)]
We actually ran into this issue in CI. NVIDIA loads some other module, but it doesn't instantly load the other module.

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=983)]
I see. Great. This is awesome. Let's delete it.

##### **Chrism** [[00:16:30](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=990)]
It does not automatically delete your instance, so you should do that.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=997)]
Deleted. Great, and I'm disconnected. That's awesome. Very cool. That's running our CI. I think we talked about all the upgrades that are going to go into CI.

##### **Chrism** [[00:16:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1011)]
You'll see there's a USB3 option there. I need to figure out what's wrong. There appears to be some issue when you run the USB device at 20 gigabits per second. I'm not sure exactly what that is.

##### **Geohot** [[00:17:08](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1028)]
I don't know about that.

##### **Chrism** [[00:17:10](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1030)]
It looks like some sort of race condition in the firmware, or maybe it's somewhere else, but I need to look some more.

##### **Geohot** [[00:17:18](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1038)]
Cool. We want to get those 5060s in the computers. For 3080s, I'd like to have a couple of tall towers that are just fourteen 3080s.

##### **Chrism** [[00:17:35](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1055)]
I think I saw one of the tall towers getting built today.

##### **Geohot** [[00:17:39](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1059)]
I think I have three machines. We can use the old cheap motherboards with fourteen 3080s, and those will be for the students.

##### **Chrism** [[00:17:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1071)]
Sounds good.

##### **Geohot** [[00:17:52](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1072)]
They're going to break all this.

##### **Chrism** [[00:17:57](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1077)]
The more you use this now, the better it'll be, because then it'll break now as opposed to breaking later.

##### **Geohot** [[00:18:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1085)]
Can agents use it?

##### **Chrism** [[00:18:07](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1087)]
Yes. If your SSH session is not interactive, it'll show you a little help, which you can also get if you do "ssh reserve help."

##### **Geohot** [[00:18:25](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1105)]
I told GLM.

##### **Chrism** [[00:18:28](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1108)]
Oh, it figured it out? Okay, cool.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1109)]
No, we'll see if it figured it out. It did something stupid to start with. Oh, "ssh reserve create 4080." Okay. Is it going to tell it how to SSH in, or is it going to be confused?

##### **Chrism** [[00:18:45](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1125)]
The thing I noticed Codex does is it opens an interactive session and then types "create," but it also works.

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1132)]
Codex is welcome to type if that's how Codex feels. Now it's checking the status. Is it going to know how to actually SSH to the machine?

##### **Chrism** [[00:19:01](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1141)]
No, probably not. I probably need to print something that says...

##### **Geohot** [[00:19:07](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1147)]
Okay, it's created. SSH into it. It didn't know to jump. This is what it's trying now. You have to jump through. Oh, it's SSHing into reserve and trying "openstack server show." Now it's trying to hack.

##### **Chrism** [[00:19:39](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1179)]
I don't think "openstack server show" is going to work, but we'll see.

##### **Geohot** [[00:19:43](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1183)]
It didn't work.

##### **Chrism** [[00:19:47](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1187)]
Okay, well, I'll print something that explains what you're supposed to do.

##### **Geohot** [[00:19:50](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1190)]
I told it now about the -J. Now it's trying to SSH in with a password.

##### **Chrism** [[00:19:59](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1199)]
It's also not going to... There's no username.

##### **Geohot** [[00:20:01](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1201)]
The username is runner.

##### **Chrism** [[00:20:04](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1204)]
I'll fix the username thing.

##### **Geohot** [[00:20:06](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1206)]
We always got to test our stuff with agents. Is nvidia-smi working? Oh, it's running hostname. I see what it's doing. Cool. With a little help, my agent's getting through, but we got to explain this to both agents and people, what the next steps are. Let's see if it figures out how to modprobe nvidia, get that up.

##### **Geohot** [[00:20:45](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1245)]
Let's do HCQ2 stuff next. What's on the agenda for HCQ?

##### **Nimlgen** [[00:20:55](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1255)]
I've been merging some quality-of-life improvements and latency improvements for HCQ2. We have VFIO now. I'm slowly pulling changes from both of our branches, both Kimi and GLM, which are related to devices and HCQ2 and all these things.

##### **Nimlgen** [[00:21:25](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1285)]
On the SSD machine, I'm hitting about 25 tokens a second now.

##### **Geohot** [[00:21:39](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1299)]
The new GPUs helped a lot?

##### **Nimlgen** [[00:21:43](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1303)]
Yeah. Having more VRAM, I can cache more experts, and at the same time I can run a speculator.

##### **Geohot** [[00:21:58](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1318)]
How much did that improve things?

##### **Nimlgen** [[00:22:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1325)]
I think just switching GPUs, it went from 14 to 18, and the rest is speculative.

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1337)]
What do we think is possible?

##### **Nimlgen** [[00:22:23](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1343)]
I'm still aiming to reach 30, stable 30, because in some benchmarks it's possible. That depends on how reusable the experts are, because sometimes I can hit 30.

##### **Geohot** [[00:22:41](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1361)]
Do we have a good speculator? I've always struggled to find good speculators for Kimi.

##### **Nimlgen** [[00:22:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1368)]
I'm just using whatever is available at Hugging Face, EAGLE or something like that.

##### **Geohot** [[00:22:59](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1379)]
Those are kind of terrible. Also, how fast can we run GLM?

##### **Nimlgen** [[00:23:08](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1388)]
I'll try that next.

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1391)]
Forget DeepSeek. Just normal GLM, or even GLM Flash. Still, 30 tokens per second would be great. This is perhaps a sellable box. I think it tests all the correct things for HCQ2 as well. How mergeable is this?

##### **Nimlgen** [[00:23:46](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1426)]
Definitely it's not mergeable in this state, but I'm slowly pulling changes. Started with HCQ2 changes.

##### **Geohot** [[00:24:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1440)]
I think this is the ultimate stress test for HCQ2. This is what it was supposed to be capable of. Being able to swap all the things and schedule all the accesses, some of them even dynamically, is exactly what we want. Is it fast to iterate on that Kimi thing?

##### **Nimlgen** [[00:24:30](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1470)]
I would say so.

##### **Geohot** [[00:24:32](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1472)]
At least you don't have to wait for the weights to load every time. That's going to be annoying to iterate on, RAM-loaded Kimi.

##### **Nimlgen** [[00:24:41](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1481)]
Currently, the best I could get it is about a minute to load the whole thing.

##### **Geohot** [[00:24:52](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1492)]
GLM Flash takes a minute too. It got a lot faster. That seems like a good project. Let's get all that stuff upstreamed, starting by upstreaming the NVMe device. Clean up HCQ. Anything else?

##### **Nimlgen** [[00:25:27](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1527)]
No, that's it for me. Also, this week I think I'll merge the multithreaded CPU back.

##### **Nimlgen** [[00:25:37](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1537)]
And paged attention, take a look into that.

##### **Geohot** [[00:25:40](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1540)]
You want to bring multithreaded CPU back?

##### **Geohot** [[00:25:43](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1543)]
I think I was too aggressive about paged attention. I don't know if we want to start messing with the MMU and doing that yet. Especially for GLM, we'll be able to fit many, many KV caches. Maybe once we get to Kimi, this is more annoying because we're more starved for... [trails off]. Cool. Assembly?

##### **Qazalin** [[00:26:14](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1574)]
This is the branch. ETA is end of week to merge it. I've cleaned it up a bunch, and it's going to work for CPU only, compiling the assembly kernels into CPU.

##### **Qazalin** [[00:26:29](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1589)]
I realized that to make the emulator fast, I needed to implement linking in tinygrad. The majority of this branch's code is cleaning up and making sure the ELF thing works. Basically, every instruction becomes its own BINARY UOp, and during runtime we link.

##### **Qazalin** [[00:27:01](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1621)]
We already have a lot of the infrastructure in place, so the changes required are pretty minimal. We don't really need a linker. We currently have something similar to a linker, so I just made a Python dictionary of the addresses.

##### **Qazalin** [[00:27:18](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1638)]
I think this is also going to help HCQ2, because HCQ2 currently has all the helpers defined at the top, and it recompiles the helpers whenever there's a user of that helper. This will cache the helpers into their own standalone binary, and at runtime it just PC-jumps into that helper's location.

##### **Geohot** [[00:27:41](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1661)]
This shouldn't be calls, right? This should just be generic relocations.

##### **Qazalin** [[00:27:50](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1670)]
Yeah, calls is a list of calls, but...

##### **Geohot** [[00:27:53](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1673)]
You're passing in... Your type is CPUProgram, right?

##### **Qazalin** [[00:27:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1676)]
Yes.

##### **Geohot** [[00:27:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1676)]
What this should be is a dictionary of names to buffers. I don't know if you're name-keying them. What this is is one-time-linked things, but it shouldn't be a CPUProgram.

##### **Qazalin** [[00:28:19](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1699)]
On TinyELF, I made the UOp. If you go to device.py, it's at the bottom. TinyELF has calls, tuple[UOp, ...]. That's a list of BINARY UOps.

##### **Nimlgen** [[00:28:50](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1730)]
You probably want to read the very bottom of hcq2, which has some linking code. That might help you implement that.

##### **Qazalin** [[00:29:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1745)]
But your linking is linking to external libraries, like gettime and stuff, right? It's not linking to internal...

##### **Geohot** [[00:29:13](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1753)]
Why does that matter?

##### **Qazalin** [[00:29:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1755)]
Those are C libraries that are external. By FFI, you call them.

##### **Geohot** [[00:29:21](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1761)]
What does that mean?

##### **Qazalin** [[00:29:22](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1762)]
When I try to integrate those into this, you think it's going to be merged into one thing? There's no difference between calling gettime versus calling...

##### **Geohot** [[00:29:33](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1773)]
What's the difference between calling a function if that function is in an external library or in a buffer you control?

##### **Qazalin** [[00:29:44](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1784)]
Both are addresses, so we just need...

##### **Geohot** [[00:29:49](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1789)]
The difference is that we control the address. If anything, it's easier to link to something that's internal. Is the HCQ2 linker fast?

##### **Nimlgen** [[00:30:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1805)]
I would say so.

##### **Geohot** [[00:30:08](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1808)]
We definitely need to solve this in one place, and we should not have two things. You think it's at the bottom of hcq2? LinkCtx, pm_link. Oh, God. Why are they typed Any?

##### **Nimlgen** [[00:30:33](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1833)]
What?

##### **Geohot** [[00:30:34](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1834)]
Why are your pattern matchers typed Any?

##### **Nimlgen** [[00:30:43](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1843)]
That's defined by backends.

##### **Geohot** [[00:30:49](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1849)]
That's not fine. We got to be careful about types and use of Any.

##### **Nimlgen** [[00:31:02](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1862)]
Basically, it's PatternMatcher or None.

##### **Geohot** [[00:31:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1865)]
You're using it in graph_rewrite, so it better be a PatternMatcher.

##### **Qazalin** [[00:31:10](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1870)]
This uses GETADDR.

##### **Geohot** [[00:31:12](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1872)]
GETADDR is fine. You probably want to use GETADDR also. You should be able to completely reuse this linker. There's absolutely no difference if you're linking to gettime versus linking to something local. The only potential difference is that you might have to keep a reference so it doesn't go out of scope.

##### **Qazalin** [[00:31:29](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1889)]
The addresses are different.

##### **Geohot** [[00:31:31](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1891)]
What do you mean the addresses are different?

##### **Qazalin** [[00:31:32](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1892)]
The references. You have to keep the address, the allocation.

##### **Geohot** [[00:31:37](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1897)]
When we link to something like gettime, how do we make sure it stays alive?

##### **Chrism** [[00:31:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1908)]
What do you mean, stays alive?

##### **Nimlgen** [[00:31:53](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1913)]
We have the fixed address during the whole runtime of tinygrad.

##### **Geohot** [[00:32:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1920)]
Where do we look these things up?

##### **Chrism** [[00:32:09](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1929)]
Which things?

##### **Geohot** [[00:32:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1931)]
Where do we look up the address of gettime? That should be... CPU execute. Oh, I see, we've improved CPUProgram. That one mprotect is a lot nicer than what we used to have.

##### **Nimlgen** [[00:33:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1991)]
Currently, the linking happens in CPUProgram.

##### **Geohot** [[00:33:16](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=1996)]
We have this whole thing called DLL. I see in CPUProgram there's a hardcoded libm. So the linking happens in CPUProgram? I don't see it.

##### **Nimlgen** [[00:34:03](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2043)]
It calls elf_loader, and elf_loader...

##### **Chrism** [[00:34:07](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2047)]
What about the linking for HCQ2?

##### **Nimlgen** [[00:34:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2051)]
...does the relocations.

##### **Chrism** [[00:34:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2055)]
For instance, if you want to do a libusb call, where does that go?

##### **Nimlgen** [[00:34:21](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2061)]
A libusb call is compiled as a simple relocation, and we just resolve that.

##### **Geohot** [[00:34:32](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2072)]
That's just resolved by the ELF loader?

##### **Chrism** [[00:34:36](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2076)]
Yeah. jit_loader, it's called.

##### **Geohot** [[00:34:41](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2081)]
I see nothing in CPUProgram doing the relocation.

##### **Nimlgen** [[00:34:50](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2090)]
It's jit_loader. It implements all relocations for CPU programs.

##### **Geohot** [[00:35:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2100)]
Oh, I see. You pass in link_libs there. You're going to want to reuse this. It shouldn't be ctypes.CDLL, but...

##### **Chrism** [[00:35:16](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2116)]
We can rewrite that. The ctypes.CDLL code is pretty old, and it might not be a horrible idea to rewrite.

##### **Geohot** [[00:35:24](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2124)]
How good is our ELF loader? This is like a universal... All of these things should be alive in the method cache, right?

##### **Qazalin** [[00:35:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2148)]
Mm-hmm.

##### **Geohot** [[00:35:49](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2149)]
You're going to want to give them the name that matches the method cache and pass in the method cache there. You shouldn't need all that stuff. You should be able to reuse this entirely.

##### **Geohot** [[00:36:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2160)]
When you compile it, there's three ways to link to something: you can hardcode the address, pass it as an argument, or use a relocation, which is actual linking, like the keyword extern in C. You can make them externs. That should just work, right? You should be able to extern anything in the method cache.

##### **Qazalin** [[00:36:31](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2191)]
I just declare this in LLVM IR.

##### **Geohot** [[00:36:33](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2193)]
Yeah, that's extern. That's the same. Then where you resolve those...

##### **Qazalin** [[00:36:39](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2199)]
Is the linker.

##### **Geohot** [[00:36:42](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2202)]
It should be the same linker, I think.

##### **Qazalin** [[00:36:46](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2206)]
I'll try reusing HCQ2.

##### **Geohot** [[00:36:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2211)]
We definitely shouldn't need to create another linker, and I don't think that should be on there either. We definitely don't want that. This should be in the [unclear] where it resolves.

##### **Nimlgen** [[00:37:24](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2244)]
For some time, we actually wanted to unwrap all this ELF information and put it on the UOps. Actually, pm_link should just resolve all this and apply all these patches to allocations, but that's probably...

##### **Geohot** [[00:37:42](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2262)]
I don't know if we have to do that right now.

##### **Qazalin** [[00:37:49](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2269)]
By method cache, do you mean the binary method cache or the...

##### **Geohot** [[00:37:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2276)]
The compiled machine code. We have some kind of cache to the machine code, right? What's that called?

##### **Qazalin** [[00:38:04](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2284)]
It's called the compile cache. It's in the compiler device... device.py, Compiler.

##### **Geohot** [[00:38:10](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2290)]
Does that actually put it on the device?

##### **Qazalin** [[00:38:12](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2292)]
It puts it on the disk cache.

##### **Geohot** [[00:38:16](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2296)]
I don't want it on the disk cache. We have something that puts it in the programs, if I remember correctly. If I compile the same program twice, it's not going to copy it to the device twice, is it?

##### **Nimlgen** [[00:38:25](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2305)]
In realize.py, we have runtime_cache, which is used for old backends like CPU.

##### **Geohot** [[00:38:34](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2314)]
runtime_cache is exactly what it should be. And then Program[Self], Program[GenericDevice]... You should be able to...

##### **Qazalin** [[00:38:52](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2332)]
Reuse the runtime.

##### **Geohot** [[00:38:54](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2334)]
Yes. What is runtime_cache? Oh, tuple[bytes, str]. It's the AST key and the device. That's basically what you'll key on. You just need some method to resolve the links. Does anything ever clear runtime_cache right now?

##### **Nimlgen** [[00:39:19](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2359)]
No.

##### **Geohot** [[00:39:20](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2360)]
Great. There's the scope issue resolved. You should be able to link to anything in runtime_cache, and this is probably useful for other things as well.

##### **Chrism** [[00:39:44](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2384)]
In conftest.py, Chenyu added something to clear runtime_cache between pytest runs, because that was what was causing us to use so much memory.

##### **Geohot** [[00:39:57](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2397)]
Oh, yeah.

##### **Qazalin** [[00:40:02](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2402)]
There is some scope issue.

##### **Geohot** [[00:40:06](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2406)]
We could even capture that at program-build time. This should not be TinyELF, right? This CPUProgram right there, that thing you're constructing in devcalls, is already a runtime.

##### **Qazalin** [[00:40:28](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2428)]
That doesn't get cleared.

##### **Geohot** [[00:40:31](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2431)]
You can hold a link to it. It should be resolved some way as method extern. I don't know exactly how we want to do it, but it shouldn't be a change... [trails off].

##### **Chrism** [[00:40:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2448)]
I think TinyELF is somewhat confusingly named because it really has nothing to do with linking.

##### **Geohot** [[00:40:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2456)]
What do you mean it has nothing to do with linking?

##### **Chrism** [[00:40:59](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2459)]
The device stuff. It's just a container format for additional binary information. At least when I originally wrote this, it had nothing to do with linking.

##### **Geohot** [[00:41:16](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2476)]
It's what I expected it to be.

##### **Chrism** [[00:41:20](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2480)]
Sure.

##### **Geohot** [[00:41:21](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2481)]
It doesn't have to do with linking. What name do you want to give it?

##### **Chrism** [[00:41:31](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2491)]
I don't have a better name, but I'm pointing out that it wasn't originally intended to do that. If you're looking at it and thinking, "That must be where the linking information goes because it's called ELF," that may not be a valid assumption.

##### **Geohot** [[00:41:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2511)]
It's not Program. I don't know. I'm not that worried about this.

##### **Qazalin** [[00:42:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2520)]
I'm just going to give it a try.

##### **Geohot** [[00:42:03](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2523)]
How are we doing on lines overall? 25,616. What are the worst offenders?

##### **Qazalin** [[00:42:30](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2550)]
It's probably going to be a lot of work.

##### **Geohot** [[00:42:42](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2562)]
Ops is the worst offender. Ops has a ton of crap in it. Someday we should figure out how to separate out the rewrite engine and the ops. How many places does it call to it? Can I put it in here? Oh, here it is. We also have to think about how to make that rewrite engine fast, how to compile UPats completely to Python.

##### **Qazalin** [[00:43:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2591)]
As one.

##### **Geohot** [[00:43:14](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2594)]
The whole pattern matcher should become one program, one function that returns a generator, and that generator is all the possible rules that match it, including all the possible permutations. Right now, we spend extra time doing permutations of the one rule, when in reality there should just be one big generator that yields every time it finds a hit. We can play with this in an LLM, maybe come up with something that's not totally trash.

##### **Geohot** [[00:43:52](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2632)]
Viz. I think it's pretty reasonable for what it does.

##### **Chrism** [[00:44:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2651)]
Are HTML files included?

##### **Geohot** [[00:44:13](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2653)]
No.

##### **Chrism** [[00:44:19](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2659)]
Is there a reason they're not?

##### **Geohot** [[00:44:24](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2664)]
I'll check the... [trails off].

##### **Qazalin** [[00:44:30](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2670)]
You can't golf HTML by putting the CSS on one line?

##### **Geohot** [[00:44:34](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2674)]
No, we don't want to golf that.

##### **Chrism** [[00:44:38](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2678)]
Right now, you could golf it by putting the JS in the HTML file.

##### **Geohot** [[00:44:43](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2683)]
Exactly. We don't do that. We do not do that.

##### **Qazalin** [[00:44:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2688)]
It has nothing in it.

##### **Geohot** [[00:44:52](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2692)]
Viz is fine. It's mostly this one file. ONNX, that's fine, probably. runtime/ops_amd. What's in here? Not even the driver. We should get some reverse-engineering LLM on... See if we really need AQL. I hate that we have to support AQL.

##### **Geohot** [[00:45:54](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2754)]
All right, my LLM kernel's trash. A lot of cleanup's possible there. I think a lot of stuff will be a lot easier to clean up after studentgrad.

##### **Geohot** [[00:46:08](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2768)]
If you saw my post... Let's talk about what I'm doing. I just work on studentgrad. Got an MNIST trainer, got a Qwen runner, got a ResNet runner. It's nice to gradually introduce all the relaxations to the rules as the weeks go on. I don't even think we're going to get to GPUs before week seven. I think in week six we'll focus on symbolic and syntactic sugar to make actual training jobs work.

##### **Geohot** [[00:46:45](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2805)]
When that's done, we'll be able to clean up the AMD kernel. Mixin, UOp...

##### **Geohot** [[00:47:07](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2827)]
Mixins are all pretty fine.

##### **Geohot** [[00:47:10](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2830)]
Shout-out to Blasty. I think we have a full boot-time and runtime trust break of the AMD GPU, specifically the PSP.

##### **Chrism** [[00:47:27](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2847)]
Can we reset them now?

##### **Geohot** [[00:47:31](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2851)]
Can we reset them? No. How's that going to work? We could exploit them to try to reset them, but I think they have to be running pretty well in order to exploit them. Actually, maybe we could root the PSP and enable the reset. It's disabled. That'd be fun.

##### **Qazalin** [[00:48:03](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2883)]
They probably reset themselves.

##### **Geohot** [[00:48:05](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2885)]
What do you mean, reset themselves? There might be some flag in the PSP that says, "Don't honor resets." I don't know. The other interesting thing is we can look into whether these GPUs can become PCIe hosts. Then we could connect a PCIe GPU to a PCIe network card. I guess we'd need something that lives in the BIOS that breaks it, but I don't know how hard that is.

##### **Geohot** [[00:48:37](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2917)]
LLM model is getting a little unwieldy, but I think it's still probably the right idea. Maybe we can cleanly break out some of these features into their own files, but probably not worth it. We should look at how other libraries are arranged. The amount of density in that file is pretty amazing, that we support so many LLMs.

##### **Geohot** [[00:49:12](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=2952)]
More viz. This could be cleaned up. These viz endpoints for the SQTT things should be simpler transformers. ops_nv, SQTT... Wow, x86 is the top renderer.

##### **Chrism** [[00:50:00](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3000)]
Why is it in its own folder called isa?

##### **Chrism** [[00:50:04](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3004)]
x86 is more than all of CStyle.

##### **Geohot** [[00:50:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3011)]
I think that isa folder needs to go. I don't know why that was there. isa needs to go.

##### **Qazalin** [[00:50:23](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3023)]
Move out isa?

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3026)]
Delete the isa folder, move `__init__.py` into x86, and move x86 into renderer. Then AMD has all this trash, but it also probably...

##### **Qazalin** [[00:50:49](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3049)]
The DSL stuff?

##### **Geohot** [[00:50:53](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3053)]
I don't know. Sort it by... Is the new emulator still using all this?

##### **Qazalin** [[00:50:58](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3058)]
The new emulator is removing the old emulator, so my line-count diff is negative. I still have the DSL stuff.

##### **Geohot** [[00:51:09](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3069)]
The DSL stuff's not that bad. The DSL stuff is the better part. It's removing the old emulator, but this is actually going to be in tinygrad proper now?

##### **Qazalin** [[00:51:22](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3082)]
The lifter? No, the lifter won't be. The ELF stuff will be. The lifter I can put inside...

##### **Geohot** [[00:51:32](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3092)]
I think we want to move the lifter in. I don't know how much we have to clean things up.

##### **Qazalin** [[00:51:38](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3098)]
The lifter can move. It's a custom kernel, similar to the AMD...

##### **Geohot** [[00:51:45](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3105)]
What do you mean by that?

##### **Qazalin** [[00:51:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3108)]
It's a huge custom kernel, right?

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3111)]
What's a custom...? I mean, the stuff that we don't have is all the emulator, the stuff that generates all those things.

##### **Qazalin** [[00:51:59](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3119)]
Absolutely. There's none of that. It's a UOp. The lifter returns a SINK for every...

##### **Geohot** [[00:52:10](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3130)]
The lifter returns a SINK. My point is there's tons of trash in that test folder. I judged that code as not worthy of merging.

##### **Qazalin** [[00:52:26](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3146)]
The instruction definitions.

##### **Geohot** [[00:52:30](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3150)]
Maybe there's not that much. disasm.py, is that just for printing?

##### **Qazalin** [[00:52:36](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3156)]
Yeah, disasm is for printing. There's also the instruction implementations.

##### **Geohot** [[00:52:41](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3161)]
Where are those? Are those already in? Where's pcode? Does that still exist?

##### **Qazalin** [[00:52:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3176)]
Of course it does.

##### **Geohot** [[00:52:58](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3178)]
No, but the pcode is autogenerated pcode. Oh, test/mockgpu. Okay, this.

##### **Qazalin** [[00:53:07](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3187)]
We can clean it up and put it in autogen.

##### **Geohot** [[00:53:12](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3192)]
You can't put it in autogen. It's not autogenerated.

##### **Qazalin** [[00:53:14](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3194)]
Oh, pcode is not autogenerated?

##### **Geohot** [[00:53:16](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3196)]
pcode.py is not autogenerated, no. But you're saying you're replacing call and emu?

##### **Qazalin** [[00:53:23](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3203)]
I'm replacing call and emu with one.

##### **Geohot** [[00:53:28](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3208)]
pcode.py is not autogenerated. We can decide whether we want to continue that pcode approach or rewrite it to something else. Did this modification lower the line count? What did I say it was before? Move x86 to renderer.

##### **Geohot** [[00:53:59](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3239)]
Another company update point: if you know about the secret project, there's been incredible progress on the secret project. We sent a PO this morning. Be excited about that. That's why we need to get our LLM stuff working really well. That's what people are going to buy these things for.

##### **Wozeparrot** [[00:54:26](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3266)]
You want to try llm.tinygrad.win?

##### **Geohot** [[00:54:31](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3271)]
Oh, it works?

##### **Wozeparrot** [[00:54:35](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3275)]
I have something up. There's a key in employees.

##### **Geohot** [[00:54:46](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3286)]
llm.tinygrad.win. I forgot about this. I'm very excited. In employees, great. It has a very official-looking API key. I forgot about that. I'm very excited about that. Are we using the Cloudflare tunnel?

##### **Wozeparrot** [[00:55:13](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3313)]
Yes. We'll try to set up the... Chris needs the DMZ stuff as well, so I've been working on the DMZ stuff.

##### **Geohot** [[00:55:22](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3322)]
We're getting "invalid API key." The first call succeeded. Oh, it forgot a letter. Stupid GLM. Do we have Kimi? I see GLM and GLM Flash.

##### **Wozeparrot** [[00:55:54](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3354)]
I just added those two for now. I can add Kimi as well.

##### **Geohot** [[00:56:06](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3366)]
Cool. Nice. If this is going to stay up, I'll turn off my other stupid forwarding.

##### **Qazalin** [[00:56:20](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3380)]
We don't have to manually tunnel?

##### **Geohot** [[00:56:24](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3384)]
I don't think so. No, we got a key. All right, let me pentest llm.tinygrad.win, see if you can access without an API key. Through tinygrad.win, let's go. What proxy are you using?

##### **Wozeparrot** [[00:56:54](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3414)]
It's custom.

##### **Geohot** [[00:56:58](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3418)]
Is it crazy? I've been talking a bunch with LLMs. There's not something we could use that'll do this?

##### **Wozeparrot** [[00:57:07](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3427)]
It's basically token routing, and we also want to do some request normalization in front of it, which means we do need to parse the requests.

##### **Geohot** [[00:57:19](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3439)]
What language is it in? Is it in some custom...? Okay, cool. Multithreaded? Multiprocess?

##### **Wozeparrot** [[00:57:35](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3455)]
No, it's async.

##### **Chrism** [[00:57:38](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3458)]
Just test it with the API key you have.

##### **Geohot** [[00:57:42](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3462)]
What's awesome about LLMs in general is the amount of data is so tiny.

##### **Wozeparrot** [[00:57:48](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3468)]
Yeah, and it's a lot of time just waiting on requests.

##### **Geohot** [[00:57:57](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3477)]
"Likely Cloudflare blocking the base Python user agent." Huh.

##### **Chrism** [[00:58:06](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3486)]
It's possible I set up some weird Cloudflare rules, because we're getting a ton of spam on the Gitea.

##### **Geohot** [[00:58:15](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3495)]
It's fine. Don't worry, GLM hacked around it.

##### **Chrism** [[00:58:21](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3501)]
Great.

##### **Geohot** [[00:58:29](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3509)]
Let's add Kimi. We should have one key for employees. I don't know if we should have separate keys for different people. We'll start with one key for employees and one key for Comma, and we'll cut them off of everything else.

##### **Wozeparrot** [[00:58:56](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3536)]
The other reason I wanted to do a custom router is that we can do request priority.

##### **Geohot** [[00:59:04](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3544)]
Is this going to go in infra or something?

##### **Wozeparrot** [[00:59:08](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3548)]
Yes.

##### **Geohot** [[00:59:11](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3551)]
Let's just put it in there. It's not long, is it?

##### **Wozeparrot** [[00:59:22](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3562)]
No, it's very short.

##### **Geohot** [[00:59:29](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3569)]
Great. Flash model handled 64 concurrent with zero errors. I love how concurrency just works.

##### **Geohot** [[01:00:13](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3613)]
Worldwide-accessible LLMs. Whatever it is, we should think about making sure we're future-proofing for when we have 10,000 concurrent people accessing that. Cool. Anyone else have anything?

##### **Geohot** [[01:00:46](https://www.youtube.com/watch?v=jvlYYYAnRvM&t=3646)]
Great. Thanks, everyone. See you next week.
