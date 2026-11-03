# 2026-11-03 Meeting

### Meeting Agenda

**Time:** new meeting #44, 11/3 12pm Hong Kong time
- company update
- MLPerf, LLM serving
- course, studentgrad, chat HTML
- AMD emulator, assembly
- float symbolic, effects
- HCQ2, NVMe
- CI VMs and boxes
- Comma, bounties, LLMs


### Audio

[Youtube Link](https://www.youtube.com/watch?v=B-m2tXbhqWA)

### Highlights

- **[Company Update](#geohot-000006)**: Announced a large haul of MI300Xs, most of which "kind of work". They are heavy enough (about "two elephants" of weight) that office floor load limits have become a real concern.
- **[Exa Box & Product Lineup](#geohot-000147)**: Exa Box preorders are open at half the price and half the FLOPS, with $5 million buying 256 MI300s. MI300s will also ship in tinyboxes and as kits for home computers, and the plan is to turn the GPUs into cash soon.
- **[GPU Binning](#geohot-000306)**: The GPUs come from AMD's return pile and will be tested and graded A/B/C/F. The best go into Exa Boxes, and the rest become kits or tinybox parts.
- **[MLPerf](#wozeparrot-000546)**: The submission is in good shape, with only minor cosmetic issues left, such as a README that still said GPT-OSS instead of LLaMA.
- **[LLM Serving](#chrism-000907)**: llm.tinygrad.win works as an OpenAI-compatible API. Comma has a key and plans a Slack bot and support bot on it, so a separate automation key plus monitoring and metadata logging are planned.
- **[GLM-5.3 Speed](#wozeparrot-001253)**: GLM-5.3 decodes at about 170 tokens/s at short context with no speculative decoding, though it falls off at longer context. The other model is just breaking 100 tokens/s with speculative decoding.
- **[Studentgrad Strict Ordering](#geohot-001700)**: Studentgrad now requires all reads and writes to be strictly ordered, tracked by an `accesses` property on the UOp. This allows O(1) or O(n) checks in place of the current O(n²) assign/ordering checks.
- **[TCC Backend](#geohot-001921)**: Proposed adding Fabrice Bellard's TCC as a C backend. Its output is slower than Clang's, but it compiles in microseconds, so the studentgrad test suite runs in half a second. This could make HCQ2 and x86 paths very fast.
- **[AMD Emulator](#qazalin-002217)**: The new emulator is merged, faster and smaller (`DEV=MOCK+AMD`). It exposed n² behavior in tinygrad, such as `.shape` via simplify in shrink and the linearizer, and slow codegen blocks further progress, with CI taking 4-5 minutes.
- **[Float Symbolic Rules](#chenyu-003240)**: Chenyu audited the symbolic rules and removed those that are technically incorrect. Two or three remain, and one of them affects fusion, so big fusions must not regress.
- **[Fast Math Mode](#geohot-003735)**: Geohot proposed a tinygrad fast-math mode that assumes finite numbers, ignores signed-zero distinctions and allows reassociation. This would settle the rules that are not strictly correct, such as x/x→1 and mul reassociation.
- **[HCQ2, NVMe & Kimi](#nimlgen-004831)**: A minimal NVMe driver and HCQ2 speedups are merged. Kimi prefill is about 80 tokens/s with no decode gain, and the next step is two SDMA queues to hit about 225 GB/s.
- **[Whale Box](#geohot-010532)**: The "whale" box has 14 R9700s and will run DeepSeek Flash and full GLM, but the BIOS won't POST with all GPUs installed. Power and rack space are tight across the CI machines.
- **[CI VMs](#chrism-010654)**: The VMs are usable now, and `shutdown` releases the reservation. Shutdown wipes the drive on next boot, and Geohot objects, wanting storage kept (with a cleanup job after 24 hours) as groundwork for a cloud service renting MI300 VMs.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=0)]
Let's get started. We can start with company updates.

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=6)]
We have a huge announcement today. I think it's time to announce it. We have come into a large quantity of MI300Xs, most of which probably kind of work.

##### **Geohot** [[00:00:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=26)]
Today I've been very stressed dealing with... Do you know that a floor in an office can only handle 50 pounds per square foot? It turns out a large amount of GPUs with heatsinks is extremely heavy. I've been dealing with that. Literally, this is MI300Xs by the pound.

##### **Chenyu** [[00:00:56](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=56)]
It's like two elephants.

##### **Geohot** [[00:00:59](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=59)]
Yeah, it's like two elephants. You got room to store two elephants? That's been stressing me out, just preparing for this massive... By the way, remember when I was so excited that we were above $5 million? "Oh, we made money." Well, we're not above $5 million anymore, but we have a large quantity of GPUs.

##### **Geohot** [[00:01:22](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=82)]
Maybe six months ago, I floated the idea of raising money, but it turns out we don't have to raise money. We got paid for the AMD contract, which was good. We had money come in, and now even more money has gone out. We have a lot of GPUs and not that much money, so soon we're going to be turning these GPUs into money.

##### **Geohot** [[00:01:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=107)]
We have a lot of ways to do it. If you're interested in an Exa Box, there's two available for preorder. We halved the price, but also halved the FLOPS, so it's kind of fair. $5 million gets you 256 MI300s. Not all the MI300s totally work. We're going to look at all sorts of binning, and they're going to be available in tinyboxes. They might even be available in kits to install in your computer. We're doing lots of work on the MI300s, but it's very stressful.

##### **Chenyu** [[00:02:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=144)]
I cannot link to the Exa Box page from anywhere.

##### **Geohot** [[00:02:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=151)]
What do you mean?

##### **Chenyu** [[00:02:37](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=157)]
I see the new tinybox with all the good stuff.

##### **Geohot** [[00:02:43](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=163)]
Oh, we don't have a link. Everything's confusing enough for the six people who actually want to preorder an Exa Box. We do have one Exa Box preorder. We're also building four of them for internal use and Comma use. Depending on how the GPU binning goes, there may be fewer. The GPU binning is going to determine a lot.

##### **Geohot** [[00:03:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=186)]
These GPUs are from the return pile. We have tested a whole bunch of them. The best ones are going to go in the Exa Boxes, and then so on down the line for the ones that will be sold to you as a kit for a very reasonable price, or we put them in tinyboxes. There's A-grade, B-grade, C-grade, and F-grade. We're going to bin them and grade them all. That's kind of what I've been thinking about.

##### **Chenyu** [[00:03:50](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=230)]
Great, sounds good. And everyone in Comma is excited about the GPUs coming?

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=240)]
From boots on the ground, are people at Comma excited about the GPUs, or are they mad?

##### **Chrism** [[00:04:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=246)]
They're certainly excited about the idea of GPUs. Everyone's starting to realize how many GPUs there are and how much of an operation this is going to be.

##### **Geohot** [[00:04:19](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=259)]
We're going to make a lot of money.

##### **Chrism** [[00:04:21](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=261)]
That's true.

##### **Geohot** [[00:04:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=264)]
Remember that half the money is Comma's, so Comma's got to get hyped. Everyone's getting on the money train. It is a lot of operational complexity, so make sure everyone's in good spirits. Remind them how great MI300s are. They're really great GPUs.

##### **Chenyu** [[00:04:45](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=285)]
Sounds good.

##### **Geohot** [[00:04:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=286)]
Two elephants. Two elephants' worth of GPUs.

##### **Chenyu** [[00:04:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=292)]
That's why you don't want to self-pickup.

##### **Geohot** [[00:04:57](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=297)]
Yes, I definitely don't want to pick them up.

##### **Chenyu** [[00:05:01](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=301)]
Anything else for the company?

##### **Geohot** [[00:05:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=306)]
One more thing: the ways you're going to be able to buy them are going to vaguely be Exa Boxes, tinybox Pros with eight of them, tinyboxes with one to four of them, and kits for your home computer with one of them. Again, no warranty from AMD. AMD was very nice to sell these to us, so we owe AMD. I think we're going to sell a product that's going to make a lot of people happy.

##### **Chenyu** [[00:05:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=336)]
Great, sounds good. Moving on, let's start with MLPerf. How's everything looking?

##### **Wozeparrot** [[00:05:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=346)]
Everything is pretty good. There are some minor cosmetic issues that people raised concerns about. Those are mostly addressed.

##### **Chenyu** [[00:05:58](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=358)]
Is there any follow-up to the GPT-OSS time thing?

##### **Wozeparrot** [[00:06:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=366)]
Nothing is happening because I think it's too much work.

##### **Geohot** [[00:06:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=373)]
It is too much work. Oh, I also saw...

##### **Chenyu** [[00:06:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=375)]
Sorry, go ahead.

##### **Geohot** [[00:06:19](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=379)]
What were the cosmetic issues?

##### **Wozeparrot** [[00:06:22](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=382)]
I typoed. When copy-pasting the READMEs, I forgot to change one of them from GPT-OSS to LLaMA. It was just that, in a script path and in a title.

##### **Chenyu** [[00:06:37](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=397)]
Cool. I saw you put in the marketing material.

##### **Wozeparrot** [[00:06:42](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=402)]
Yes. Does anyone else want to join the marketing press briefing? I think George is on that.

##### **Geohot** [[00:06:50](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=410)]
What do you mean? What is it?

##### **Chenyu** [[00:06:54](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=414)]
Remember the 300-letter essay you can put with your results, or something like that?

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=420)]
Just write a nice essay about how we're super happy with AMD and their great, powerful GPUs.

##### **Wozeparrot** [[00:07:11](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=431)]
No, there's this press briefing.

##### **Chenyu** [[00:07:14](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=434)]
We can change it a bit. I think the current version is something, something, "we democratize," something, something.

##### **Wozeparrot** [[00:07:23](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=443)]
Yes. I just took our old one.

##### **Chenyu** [[00:07:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=446)]
I remember that from two years ago.

##### **Geohot** [[00:07:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=448)]
Wonderful. Except we're huge fans of AMD, so we do everything to hype up our boy AMD, who sold us two elephants' worth of GPUs.

##### **Chenyu** [[00:07:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=458)]
I don't know. I think we'll...

##### **Geohot** [[00:07:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=460)]
We'll do whatever you want. I'm not picky about this.

##### **Chenyu** [[00:07:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=466)]
Then there's the press briefing thing. You can also participate in the press briefing.

##### **Geohot** [[00:07:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=473)]
What does that mean?

##### **Wozeparrot** [[00:07:54](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=474)]
It's a big call that you join, and there's a bunch of press people.

##### **Chenyu** [[00:08:01](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=481)]
Anything you say may or may not be included in whatever announcement.

##### **Geohot** [[00:08:07](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=487)]
They're going to read you Miranda rights. Sure, if it's at a reasonable Hong Kong time, I'll join. If it's like two in the Hong Kong morning, I'm out.

##### **Chenyu** [[00:08:25](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=505)]
You'll probably check your email or something.

##### **Wozeparrot** [[00:08:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=511)]
I need to add you to the spreadsheet if you want to do it.

##### **Geohot** [[00:08:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=518)]
Okay, you can add me.

##### **Wozeparrot** [[00:08:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=520)]
Oh, it's at 1 a.m. Hong Kong time.

##### **Geohot** [[00:08:44](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=524)]
All right, enjoy.

##### **Chenyu** [[00:08:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=527)]
We never participate in the press thing.

##### **Geohot** [[00:08:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=532)]
If it was during the daytime, but no.

##### **Chenyu** [[00:08:56](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=536)]
Cool. How has llm.tinygrad.win been?

##### **Wozeparrot** [[00:09:05](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=545)]
Good.

##### **Chrism** [[00:09:07](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=547)]
It works. I think Comma wants to use it for a lot of stuff now.

##### **Wozeparrot** [[00:09:11](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=551)]
Comma has a key.

##### **Chrism** [[00:09:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=553)]
Be warned, because they have some new Slack bot that's going to reply to stuff, powered by that, and they have some new support bot. Be ready to have a lot of users, I guess.

##### **Wozeparrot** [[00:09:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=568)]
I see. We're becoming a real inference provider.

##### **Geohot** [[00:09:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=571)]
We are, and we got to get some monitoring and metadata logging up.

##### **Wozeparrot** [[00:09:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=578)]
Yes, I'll work on it.

##### **Chrism** [[00:09:41](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=581)]
We may want to have another key for these automated tasks that Comma wants to run.

##### **Wozeparrot** [[00:09:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=593)]
That's doable.

##### **Chrism** [[00:09:57](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=597)]
If we make another one and send it in their Slack, we can tell them to start using that instead for the automated stuff.

##### **Geohot** [[00:10:04](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=604)]
That's fine.

##### **Chenyu** [[00:10:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=608)]
Is there a README somewhere for how I can use this?

##### **Wozeparrot** [[00:10:16](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=616)]
It works like all the other OpenAI APIs. Just point your agent at it.

##### **Chenyu** [[00:10:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=624)]
I will figure this out.

##### **Wozeparrot** [[00:10:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=627)]
The code's in infra.

##### **Geohot** [[00:10:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=629)]
It's very simple. An agent can query it and add all the models to it if you want.

##### **Chenyu** [[00:10:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=647)]
Oh, this is different from the freegpt.party thing.

##### **Geohot** [[00:10:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=652)]
freegpt.party is just a frontend. It defaults to some inference provider that isn't ours. It's simply a one-page HTML frontend. The link I posted in the employees channel uses llm.tinygrad.win as the provider.

##### **Chenyu** [[00:11:14](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=674)]
I see. That's the key.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=679)]
The employees one has the key. I have that bookmarked on my phone. I've started using it instead of ChatGPT. It's good.

##### **Chenyu** [[00:11:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=687)]
Ours is running GLM or Kimi?

##### **Geohot** [[00:11:32](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=692)]
You got all three. Click the employees link. I'm also going to add 3.8 Flash.

##### **Chenyu** [[00:11:48](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=708)]
I opened the employee link, but it was GLM-5.3. Oh, I see the three.

##### **Geohot** [[00:12:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=722)]
I defaulted to Flash because Flash is very fast. By the way, that Flash is running on a tinybox red Flash, an actual minimum-spec tinybox red Flash that you can buy for $22,000. Claude put a lot of work into that server before I got soft-banned from Claude.

##### **Wozeparrot** [[00:12:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=747)]
You got soft-banned from Claude?

##### **Geohot** [[00:12:30](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=750)]
I didn't get soft... I don't know what happened. Pi kept retrying to compact the context and used up all my week's usage limit in half an hour.

##### **Wozeparrot** [[00:12:43](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=763)]
Interesting.

##### **Geohot** [[00:12:44](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=764)]
Now my alt account is proxied, so that won't happen again. I don't know what happened.

##### **Wozeparrot** [[00:12:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=773)]
On the LLM side, I have GLM-5.3. On short context, I'm at 170 tokens a second. Longer context still falls off a bit.

##### **Geohot** [[00:13:09](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=789)]
How about prefill?

##### **Wozeparrot** [[00:13:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=793)]
I haven't been focusing on prefill, just decode. This is 170 tokens a second, no speculative decoding.

##### **Geohot** [[00:13:21](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=801)]
That's pretty good then. What do we have now on the other one?

##### **Wozeparrot** [[00:13:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=809)]
I think we're just breaking 100 tokens a second with speculative.

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=814)]
If you have 170 without speculative, that's probably good enough.

##### **Wozeparrot** [[00:13:39](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=819)]
I looked into what the other servers are doing and what your PR does for multiuser, and how to manage that. I don't know if the way you did it is the best way.

##### **Geohot** [[00:13:59](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=839)]
I didn't do it. Claude did it. I honestly don't know what's in there.

##### **Wozeparrot** [[00:14:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=842)]
It's a mixture between how SGLang and llama.cpp do it. It's not the greatest way. I need to look more into it this week. This whole multiuser scheduling side gets pretty complex.

##### **Geohot** [[00:14:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=857)]
My understanding of the basics is that prefill is still single-user, and then for decode, you can widen the batch size.

##### **Wozeparrot** [[00:14:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=868)]
Prefill is kind of single-user, but a lot of servers still batch that.

##### **Geohot** [[00:14:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=878)]
We should look into why. At least with GLM, we have plenty of RAM. You can move to tinyamd4 if you want.

##### **Wozeparrot** [[00:14:48](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=888)]
The only annoying thing is that the FP8 spec changes between CDNA3 and CDNA4.

##### **Geohot** [[00:15:01](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=901)]
Does that really make a difference?

##### **Wozeparrot** [[00:15:04](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=904)]
I don't think it does, but at least the way the weights are encoded...

##### **Geohot** [[00:15:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=915)]
Really?

##### **Wozeparrot** [[00:15:19](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=919)]
It's fairly easy to convert between the two. It's not that big of a deal.

##### **Geohot** [[00:15:23](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=923)]
It should be plenty fast when you do the local load to convert. We don't have to push to FP4. We'll keep our stuff in FP8. I guess that won't work for Kimi, but you can do FP8 GLM on the MI3 device.

##### **Geohot** [[00:15:49](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=949)]
We should work on upstreaming whatever we can from that PR, because I eventually want to get this all upstreamed.

##### **Wozeparrot** [[00:16:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=962)]
I want to look into upstreaming some of the multiuser stuff. I do still need to figure that out, though.

##### **Chenyu** [[00:16:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=975)]
Sounds good. Let's move on. Course?

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=983)]
I got to sign my employment paperwork right now. I'm officially employed at CMU. Studentgrad is pretty close to tinygrad. My new studentgrad implementation is like 650 lines, and it's given me a real opportunity to reconsider a lot of the decisions we've made in tinygrad. Some of them are very good. The only thing we're still doing wrong is finally answering the question about assign and ordering.

##### **Geohot** [[00:17:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1020)]
I have a really good way of solving it now: all reads and writes need to be strictly ordered with respect to each other. There's no more stuff like you have to have an AFTER, and it reads that version. That turns out to be really hard to write. The relatively simple thing to write is: you're allowed to do a group of reads, and reads can be unordered with respect to each other. Then you do a write, then another group of reads, then a write.

##### **Geohot** [[00:17:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1056)]
I have this property called accesses. It's a property on the UOp that shows the whole access history of any buffers. It makes sure that when you hit a merging point, the access histories are compatible. It's no longer a valid graph to add before and after an AFTER. Everything needs to be strictly ordered.

##### **Geohot** [[00:18:03](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1083)]
In practice, I think this is going to affect almost no graphs. If you do run into a problem, you can add a STAGE and remove the problem. It lets you do basically O(1) checks, or O(n) checks. Right now we have a lot of O(n squared) checks to check for assign, read-after, use-after-self-assign kinds of things. This accesses thing was the big victory on studentgrad this week.

##### **Geohot** [[00:18:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1126)]
I'm halfway through week four of the course on my reimplementation, where I'm doing everything by hand and making sure this is actually reasonable.

##### **Chenyu** [[00:19:01](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1141)]
I saw that you removed trunc. You don't like trunc?

##### **Geohot** [[00:19:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1148)]
I don't think we should remove trunc in general. I just removed it from studentgrad because... That's the other thing I should talk about: we should add support in tinygrad's C backend for TCC.

##### **Geohot** [[00:19:21](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1161)]
TCC is Fabrice Bellard's C compiler. The outputted code is a good bit slower than Clang, but it's extremely fast to compile. We can use this for HCQ2 stuff and make HCQ blazingly fast. We always ask, "Why is x86 slow?" Use TCC and it is so fast.

##### **Geohot** [[00:19:45](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1185)]
It does a thousand studentgrad tests in under half a second, with everything: parsing, compilation, and testing. The entire studentgrad test suite runs in half a second, single-threaded. We're measuring compilation times in microseconds, not milliseconds.

##### **Geohot** [[00:20:09](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1209)]
I removed trunc because it required linking to libm. Studentgrad also doesn't have sin, log, and exp. Trunc is okay to have. The reason I don't have sin, log, and exp is that they don't have IEEE standards. Trunc does have an IEEE standard, so correctness is not an issue, but it's not an instruction on x86. Or maybe it is, but you have to link to libm. That's why I got rid of it. It doesn't really matter for the course. You can emulate trunc with a cast to int.

##### **Geohot** [[00:20:51](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1251)]
Is there a reason you want to keep it?

##### **Chenyu** [[00:20:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1255)]
Because the cast to int is wrong.

##### **Wozeparrot** [[00:20:57](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1257)]
We went over this before, I believe. We ran into this, and this is why we added trunc back.

##### **Geohot** [[00:21:03](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1263)]
I understand that it's wrong, but it's good enough for...

##### **Chenyu** [[00:21:11](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1271)]
I think for the course it's fine.

##### **Geohot** [[00:21:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1273)]
For the course it's fine. We might add it in later weeks. When we add GPUs, maybe we'll add trunc, sin, exp, all those things.

##### **Chenyu** [[00:21:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1284)]
Not directly related, but our exp is also kind of bad because we have exp2. I can talk more when I do numerics, but that's causing some big ULP issues that I don't know if we want to solve.

##### **Geohot** [[00:21:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1307)]
Whatever you want there. Chat HTML is just freegpt.party. Very popular.

##### **Chenyu** [[00:21:59](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1319)]
Sounds good. Anything else?

##### **Geohot** [[00:22:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1328)]
Nope.

##### **Chenyu** [[00:22:11](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1331)]
Moving on, AMD emulator and assembly.

##### **Qazalin** [[00:22:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1337)]
The new emulator is merged. It's a bit faster and fewer lines than the old emulator. You can check it out if you do MOCK plus AMD. I'm working on new simplifications to add to the emulator. This is the PR I'm working on right now. It's blocked by codegen being slow. There's nothing wrong with it; the emulator does it at a scale where I found n-squared behavior in tinygrad. For example, accessing uop.shape is n-squared, and our linearizer can get n-squared in some cases.

##### **Geohot** [[00:23:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1382)]
How is accessing uop.shape n-squared?

##### **Qazalin** [[00:23:05](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1385)]
Because we call simplify in...

##### **Geohot** [[00:23:09](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1389)]
We call simplify in shape?

##### **Qazalin** [[00:23:11](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1391)]
In shrink.

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1391)]
Oh, in shrink.

##### **Qazalin** [[00:23:12](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1392)]
I have a PR open that shows the reproducer. If you call shrink in a loop and then access .shape, it grows n-squared because we have .simplify.

##### **Geohot** [[00:23:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1411)]
These are all the things that hopefully studentgrad will let us clean up. We shouldn't be using simplify.

##### **Qazalin** [[00:23:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1416)]
Studentgrad is recursion-limited, though, if I try that.

##### **Geohot** [[00:23:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1420)]
Studentgrad is recursion-limited, but everything should be within bounds. I'm not going to make students write the other version. Studentgrad has a very simple pipeline rewrite that's recursive. This isn't a test of, "Can you write enterprise algorithms?" It's a test of, "Do you understand what it does?"

##### **Qazalin** [[00:24:07](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1447)]
The emulator compiles the entire program into one.

##### **Geohot** [[00:24:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1455)]
If we can find n-squared behavior, we should fix it. Do we need simplify in shrink still?

##### **Qazalin** [[00:24:20](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1460)]
Do we need simplify in shrink?

##### **Geohot** [[00:24:22](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1462)]
We shouldn't anymore. Since I've changed the API, we shouldn't need it anymore.

##### **Chenyu** [[00:24:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1469)]
Probably not shrink, but something else.

##### **Geohot** [[00:24:35](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1475)]
That comes from the era where shrink was not offset and shape.

##### **Chenyu** [[00:24:42](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1482)]
It's now shape. The shape length is encoded in one of the args, so it should be something else.

##### **Qazalin** [[00:24:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1493)]
I'll try removing it.

##### **Geohot** [[00:24:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1495)]
When shrink used to be the beginning and the end, you had to simplify to recover the shape, but now we just have the shape. That should be no problem anymore.

##### **Qazalin** [[00:25:05](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1505)]
Right now, the emulator takes four to five minutes in CI, and basically it's just codegen.

##### **Geohot** [[00:25:21](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1521)]
Further progress is blocked by that.

##### **Chenyu** [[00:25:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1531)]
It also calls resolve, and resolve calls simplify. We've probably done something stupid, and we should fix those.

##### **Qazalin** [[00:25:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1546)]
This PR you're looking at right now is working around the linearizer being n-squared.

##### **Geohot** [[00:25:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1555)]
The linearizer is n-squared too?

##### **Qazalin** [[00:25:56](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1556)]
Yes. Look at the Actions. It's timing out right now.

##### **Geohot** [[00:26:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1560)]
Why is the linearizer n-squared?

##### **Qazalin** [[00:26:03](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1563)]
Because it calls sorted recursively in the loop. You can check it. The change is so simple, like one line.

##### **Geohot** [[00:26:16](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1576)]
The change to fix it?

##### **Qazalin** [[00:26:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1577)]
Yes. Codex wrote it, and I have to really understand it.

##### **Geohot** [[00:26:23](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1583)]
Where is it calling it?

##### **Qazalin** [[00:26:25](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1585)]
There's a sort. You have to sort it.

##### **Geohot** [[00:26:33](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1593)]
That shouldn't be n-squared. That should be n.

##### **Qazalin** [[00:26:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1596)]
That's n-squared, it turns out.

##### **Geohot** [[00:26:41](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1601)]
Oh, because of tuplize. You're right. That is n-squared. Oh, my God.

##### **Qazalin** [[00:26:45](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1605)]
Codex fixed it as a class.

##### **Geohot** [[00:26:51](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1611)]
Wait, tuplize should only construct... It's probably traversing in a really bad order. Maybe try making tuplize a recursive_property instead of cached_property.

##### **Qazalin** [[00:27:04](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1624)]
Does that fix it? Part of the reason _shape is n-squared is recursive_property.

##### **Geohot** [[00:27:12](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1632)]
Oh.

##### **Qazalin** [[00:27:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1633)]
The problem with a lot of these is similar to the problem we had with without_after and src_without_body. It traverses stuff it doesn't need to traverse.

##### **Geohot** [[00:27:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1646)]
None of this should make it n-squared. Recursive_property is just straight-up O(n).

##### **Qazalin** [[00:27:32](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1652)]
The n-squared problem is the simplify issue, but recursive_property can make things slower.

##### **Geohot** [[00:27:39](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1659)]
Slower, but it shouldn't change the complexity.

##### **Qazalin** [[00:27:42](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1662)]
Correct.

##### **Geohot** [[00:27:43](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1663)]
This tuplize cached_property might be doing something stupid. I don't really believe that's n-squared.

##### **Qazalin** [[00:27:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1675)]
It is n-squared. I have proof. The proof is CI is timing out on my PR.

##### **Geohot** [[00:28:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1682)]
That could be for many reasons. That's not proof that this particular line is n-squared.

##### **Qazalin** [[00:28:07](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1687)]
I profiled this, and the linearizer was slow.

##### **Geohot** [[00:28:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1690)]
The linearizer might be slow, but why do you think it's this line?

##### **Qazalin** [[00:28:14](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1694)]
When I fixed that, it fixed the issue.

##### **Geohot** [[00:28:16](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1696)]
Oh, because sorted is doing compares, and each compare is n-squared.

##### **Qazalin** [[00:28:22](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1702)]
The fix is to wrap it in a class with its own comparison.

##### **Geohot** [[00:28:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1709)]
I think I might have seen that before. Maybe the better solution is to look into removing tuplize. Why do we need that?

##### **Qazalin** [[00:28:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1718)]
It gives a nice order, quote-unquote. Ideal order, quote-unquote.

##### **Geohot** [[00:28:44](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1724)]
What if we just remove it?

##### **Qazalin** [[00:28:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1726)]
Is it Tom's creation?

##### **Geohot** [[00:28:48](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1728)]
No, I wrote it.

##### **Chenyu** [[00:28:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1732)]
Removing it would be nice, because I believe there are some flaky tests if you set it to zero or something.

##### **Geohot** [[00:29:01](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1741)]
That's a problem. That's a bug.

##### **Chenyu** [[00:29:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1746)]
We all agree bad complexity and stupid things need to be fixed.

##### **Geohot** [[00:29:16](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1756)]
Removing tuplize would be a win.

##### **Qazalin** [[00:29:19](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1759)]
The emulator has some adversarial graphs that really show...

##### **Geohot** [[00:29:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1767)]
We shouldn't patch this over with more complexity. We should figure out why we need tuplize in the first place. I'm not sure why it's there. Removing tuplize would be a good victory.

##### **Qazalin** [[00:29:41](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1781)]
You can also look at the base of the emulator.

##### **Geohot** [[00:29:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1787)]
In master?

##### **Qazalin** [[00:29:49](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1789)]
Yes, in master.

##### **Geohot** [[00:29:59](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1799)]
DEV equals MOCK plus AMD. Also use... test GEMM?

##### **Qazalin** [[00:30:09](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1809)]
Use Clang, because by default...

##### **Geohot** [[00:30:12](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1812)]
Also use Clang. What's the syntax for that? I don't remember.

##### **Qazalin** [[00:30:20](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1820)]
A semicolon, and then CPU:CLANG.

##### **Geohot** [[00:30:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1824)]
I have to put this in quotes.

##### **Chrism** [[00:30:30](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1830)]
If you have better ideas for what it looks like, we can change it.

##### **Qazalin** [[00:30:35](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1835)]
The annoying thing is that you have to put quotes.

##### **Geohot** [[00:30:42](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1842)]
Emu. Get the source. Wait, structs are gone?

##### **Qazalin** [[00:30:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1853)]
Structs are gone, yeah.

##### **Geohot** [[00:30:57](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1857)]
Nimlgen?

##### **Qazalin** [[00:30:58](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1858)]
Thank you, Nimlgen.

##### **Geohot** [[00:31:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1862)]
Nimlgen giveth and Nimlgen taketh away.

##### **Qazalin** [[00:31:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1870)]
You see how it's doing the loads outside the calls.

##### **Geohot** [[00:31:16](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1876)]
It's removing the... That's nice. You're close to being able to make SGPRs individual ALLOCs, and then they can be REG. Instead of having this plus, you could directly pass in SGPR 126.

##### **Qazalin** [[00:31:51](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1911)]
Currently, the lift is still slow because it's trying to emulate... Imagine emulating 16 threads in one thread. I have to figure out how to parallelize stuff.

##### **Geohot** [[00:32:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1928)]
You'd have to recover the warp dimension of it. No rush on that. Things like removing tuplize...

##### **Chenyu** [[00:32:34](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1954)]
Anything else?

##### **Qazalin** [[00:32:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1956)]
No, that's all.

##### **Chenyu** [[00:32:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1960)]
Moving on, next is my stuff. I went through all the symbolic rules, found the ones that are technically incorrect, and tried to remove them. If the result seems fine, I just merge it. For now, we have probably two or three that are still technically incorrect, but I don't have a good way to fix them right now.

##### **Chenyu** [[00:33:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=1995)]
The current symbolic rules should read nicer. I'll figure out the rest. In one case, it affects fusion, which is annoying. We definitely don't want to regress any big fusion.

##### **Chenyu** [[00:33:42](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2022)]
Another is the exp thing I just mentioned. Our primitive for gradient is exp2, so we multiply by a constant, and our derivative is exp2 working with another constant. Should these two constants cancel out? Currently we cancel the one for exp but not for log, which is already pretty weird. If we want to cancel this out and have the rules be correct, the best solution I have is exp as an op just for gradient, and remove that right after gradient. The gradient for exp is exp, so we don't have this constant shenanigan.

##### **Chenyu** [[00:34:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2078)]
Our exp also passes through exp2. If you do exp(120) or something, you have a really big ULP difference. I don't know if we care enough to fix it.

##### **Geohot** [[00:35:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2108)]
Shouldn't the log2 and the opposite of log2 cancel out?

##### **Chenyu** [[00:35:18](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2118)]
No. Canceling out is wrong. You cannot just say those two are the same, so the div becomes one, because that's not correct for inf.

##### **Geohot** [[00:35:30](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2130)]
How much do we care?

##### **Chenyu** [[00:35:35](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2135)]
That's what I mean. That's how I arrived at our current state.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2140)]
I definitely care about not having more UOps versus inf.

##### **Chenyu** [[00:35:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2152)]
Currently my principle is: I know the set of rules that are technically not correct, and I'll find ways to work around those. Float divided by itself, can we replace that with one? Currently, no. We also don't allow reassociating adds. (a + b) + c is different from a + (b + c). But we currently allow that for mul, because otherwise we have more constants that won't cancel out.

##### **Geohot** [[00:36:43](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2203)]
What we probably want is fast math. Every compiler kind of does this. They have an option to enable rules that are technically wrong but fine in most cases.

##### **Chenyu** [[00:36:56](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2216)]
My strategy is to think more around these. It's not very clear how to handle it. It's not a big deal; it's more of a principle thing versus the number of ops versus the output quality of the code.

##### **Geohot** [[00:37:18](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2238)]
This is the way every compiler deals with this kind of stuff. There's a flag.

##### **Chenyu** [[00:37:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2248)]
We disable all the fast math on every backend because they always do things slightly differently.

##### **Geohot** [[00:37:35](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2255)]
We want a tinygrad mode that is fast math. It assumes numbers are finite, strips out signed-zero distinctions, and permits reassociating math operations.

##### **Chenyu** [[00:37:51](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2271)]
Anyway, that's a thread I'm working on.

##### **Geohot** [[00:37:58](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2278)]
The ideal thing is to quantify all of this. If some tests require fast math off, we turn fast math off. Hopefully we can propagate this through everything so we could reenable it on the backends too. We'll think more about this.

##### **Chenyu** [[00:38:18](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2298)]
So far, the changes I merged are the ones I think are nice. Some of those rules aren't making anything better and are just wrong, so getting rid of those is nice.

##### **Geohot** [[00:38:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2318)]
I see group-up effects too, and we have this AFTER merger thing. We can go further than that. What I'm going to play with in studentgrad is pushing AFTERs down. If you have an AFTER on an ADD, there's no reason you can't push that AFTER after the ADD, because the ADD has no side effects.

##### **Chenyu** [[00:39:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2340)]
A lot of this is motivated by studentgrad. I read how the current rules and implementation look. One big difference is that studentgrad currently doesn't have simplifying rules that can drop an effect. You don't have anything like multiply by zero.

##### **Geohot** [[00:39:30](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2370)]
I also have the rewrite studentgrad, and in rewrite...

##### **Chenyu** [[00:39:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2378)]
Sorry, go ahead.

##### **Geohot** [[00:39:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2380)]
If I have x times zero equals zero, instead of replacing x times zero with zero, I replace it with zero AFTER x.

##### **Chenyu** [[00:39:49](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2389)]
There's a very big essay I had for the reasons this doesn't quite work. It's kind of annoying.

##### **Geohot** [[00:40:04](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2404)]
Why doesn't this work? I'm depending on this for studentgrad.

##### **Chenyu** [[00:40:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2410)]
It probably works for studentgrad. "Doesn't work" is more of an implementation limitation. For these things to merge in tinygrad, all the existing AFTER stuff also needs to work for now. It's crashing somewhere.

##### **Geohot** [[00:40:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2428)]
I very much believe tinygrad has bugs that don't implement this correctly. Some of my studentgrad tests... Astra is very smart and came up with some very smart tests.

##### **Chenyu** [[00:40:42](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2442)]
Just for fun, currently all except 70 tests...

##### **Geohot** [[00:40:49](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2449)]
In tinygrad? Nice.

##### **Chenyu** [[00:40:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2453)]
I guess 90 don't pass, but 18 of them are numerical decisions studentgrad picks that don't make sense, so we think that's fine.

##### **Geohot** [[00:41:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2468)]
There are a few annoying things, particularly around div.

##### **Chenyu** [[00:41:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2475)]
Div and a lot of undefined... For some reason, the min is bad, so we don't use min.

##### **Geohot** [[00:41:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2486)]
Mean or min?

##### **Chenyu** [[00:41:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2487)]
For many weird integer behaviors, studentgrad just picks INT_MIN.

##### **Geohot** [[00:41:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2496)]
Yes. I pick INT_MIN for all. That's what x86 does also.

##### **Chenyu** [[00:41:44](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2504)]
I understand. I surveyed all the common hardware and compiler behavior, and that's what x86 does, but not anything else.

##### **Geohot** [[00:41:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2515)]
I'm open to changing it.

##### **Chenyu** [[00:42:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2520)]
Those are just specs for weird behavior, so those don't count in the 70. A lot of the 70 are the STORE/AFTER thing we mentioned, and the effect-removing part. My focus this week is to reconcile more of this and come up with something more principled.

##### **Geohot** [[00:42:32](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2552)]
The most interesting difference is that accesses thing too. I don't have it totally worked out. I should finish week four first, but if you look at the accesses property in rewrite, it's enforcing that strict ordering of loads and stores I was talking about.

##### **Chenyu** [[00:42:51](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2571)]
A lot of interesting things happen with images. IMAGE caused some issues. I need to check the latest version of your thing, but image fusing and memory coalescing... Some of the model doesn't directly translate.

##### **Geohot** [[00:43:14](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2594)]
I also allow returning pointers from calls.

##### **Chenyu** [[00:43:23](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2603)]
That made CALL an effect, right?

##### **Geohot** [[00:43:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2608)]
CALL always had an effect. As long as you can have stores inside a CALL, CALL has an effect. In that accesses thing, I'm also careful to do alias analysis. I make sure pointers written to by calls can't be aliased.

##### **Chenyu** [[00:43:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2632)]
I see.

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2633)]
You can't pass in the same buffer, or any view of the same buffer, twice. I still got to finish that rewrite, but it's really making everything tight. There's stuff in the source compiler I don't understand, but there's nothing in rewrite I don't understand. I can fully describe each one of those properties from memory.

##### **Chenyu** [[00:44:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2657)]
Effect is my attempt to translate this concept, make it work, and make every rule actually depend on effects, not yet another small set of UOps I cannot understand. I hope this will bring us to a better state.

##### **Geohot** [[00:44:39](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2679)]
What you're missing from effect is RANGE and END. You can decide if you want to include those.

##### **Chenyu** [[00:44:51](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2691)]
Currently I don't. When we care about loads for now, it's a union. Same for AFTER in some cases, just union loads.

##### **Geohot** [[00:45:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2702)]
RANGE and END can have effects. In many ways, BARRIER is END.

##### **Chenyu** [[00:45:09](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2709)]
There's BARRIER. We also don't know how much we know or have decided on atomics. That's another one.

##### **Geohot** [[00:45:18](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2718)]
We're going to need some kind of atomic thing.

##### **Chenyu** [[00:45:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2724)]
It seems commonly used. Similarly, there's WMMA working with a warp. There are some weird cases for what effect really should be.

##### **Geohot** [[00:45:37](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2737)]
WMMA can become a CALL. I fully understand what MULTI is going to be. I'm going to add MULTI to studentgrad. It's very simple: it's just STAGE. All MULTI is is STAGE on the device range.

##### **Geohot** [[00:45:50](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2750)]
You can't actually render a STAGE on a device range, because what device are you staging it to? There's no device. Studentgrad has three ways to end ranges: STAGE, REDUCE, and END. If you stage a device, it goes on some virtual device that's a merger of all of them. You have to process it and remove that device range and actually render it. The same thing is true for warps. It's identical.

##### **Chenyu** [[00:46:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2786)]
I see.

##### **Geohot** [[00:46:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2788)]
I've also solved the problem of the ranges. We had this annoying thing where I wasn't sure how to deal with MULTI and CALLify. My solution is very simple: you can use BUFFER anywhere, in any CALL, and it is global. That means you're in no rush to remove buffers from calls.

##### **Geohot** [[00:46:58](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2818)]
If you have BUFFER in some CALL nested five deep, we'll have a pass that recursively removes that BUFFER from the CALL, turns it into a PARAM, and puts it on the outer CALL. This solves the interaction between CALLify and MULTI, if that makes sense.

##### **Chenyu** [[00:47:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2846)]
Not fully, but I'll read studentgrad later.

##### **Geohot** [[00:47:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2851)]
The only thing to take away is BUFFER can go inside any CALL depth, and it is truly global.

##### **Qazalin** [[00:47:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2858)]
The reason we have it the other way is caching, right? We're in a rush to remove BUFFER so that we can cache it.

##### **Geohot** [[00:47:45](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2865)]
You still want to remove BUFFER, but we can wait until after we do MULTI or rangeify too. For caching, you don't actually have to remove the buffers. You can renumber the buffers to something canonical and then hash them. I think that's a much better way to do it.

##### **Chenyu** [[00:48:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2895)]
That's pretty much my stuff. With that, we can move on to HCQ2 and NVMe.

##### **Nimlgen** [[00:48:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2911)]
For the Kimi project, not any gains for decode speed. Prefill speed is about 80 tokens a second. I merged some HCQ2-related speedups and a minimal implementation of the NVMe driver.

##### **Nimlgen** [[00:48:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2935)]
I'll focus on speed next. The current implementation is pretty slow. We completely use MEC or SDMA queues to access NVMe drives. We use the queue to copy commands onto the NVMe. To hide latency, we need to use two SDMAs to get the full speed, those 225 gigabytes a second. I'll probably focus on this this week.

##### **Geohot** [[00:49:39](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2979)]
You need both SDMAs to get the speed? Isn't the drive the one initiating the DMA?

##### **Nimlgen** [[00:49:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=2992)]
Yes, but we put commands into the drive from the GPU. It could be MEC, not SDMA queues. We encode everything onto the GPU, and the GPU is the scheduler for the drives. When it needs data, it writes the command into the drive ring, and we read that data into GPU VRAM.

##### **Geohot** [[00:50:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3029)]
That makes sense, but why do you need two SDMAs to keep up? Is the block size not big enough, or is it a latency-hiding problem?

##### **Nimlgen** [[00:50:39](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3039)]
It's a latency-hiding problem. With one SDMA, I can get up to 210 gigabytes a second, maybe 200 in more realistic scenarios. To get another 25 gigabytes, I'll try, but currently I can reach that with two different engines only.

##### **Geohot** [[00:51:12](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3072)]
Let's publish some benchmarks. These might be some of the fastest. For a single computer, this has to be the fastest storage array in the world.

##### **Nimlgen** [[00:51:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3088)]
Once it merges into master, I'll share some benchmarks.

##### **Geohot** [[00:51:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3096)]
What's still missing from what's in master now?

##### **Nimlgen** [[00:51:41](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3101)]
We have all the core implementation. The only thing missing is speed improvements, basically the two-SDMA implementation.

##### **Geohot** [[00:51:52](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3112)]
Even 210 is a brag.

##### **Nimlgen** [[00:52:03](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3123)]
For Kimi and the other changes, most are in the LLM directory. There are a bunch of custom kernels, and some have intersections with your branch. Do we want to pull those? Particularly, I'm interested in the faster all-reduce as well.

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3156)]
Again, being honest about that branch: Claude wrote it, and I don't know what's in there. Everybody should take out the pieces they want. If there's good all-reduce stuff, take it and merge it.

##### **Geohot** [[00:53:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3193)]
Sorry, my mic just froze. If you think there's good stuff, take it out, clean it up, and merge it.

##### **Nimlgen** [[00:53:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3206)]
I'll take a look into that.

##### **Geohot** [[00:53:30](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3210)]
That's where I want tinygrad to be by the end of the year on master: doing what that branch is doing now, having a runnable version of all these LLMs across a wide variety of hardware. RDNA3, RDNA4, CDNA.

##### **Geohot** [[00:53:56](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3236)]
For prefill, we should be able to go a lot faster, right?

##### **Nimlgen** [[00:54:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3242)]
I think so. Definitely faster than 80 tokens a second.

##### **Geohot** [[00:54:16](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3256)]
We shouldn't be RAM-limited at all. Sure, we got to read the whole model, one read of the whole model.

##### **Nimlgen** [[00:54:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3268)]
I'll take a look into that.

##### **Geohot** [[00:54:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3280)]
We're getting another Kimi box built. Anything else I can do to help?

##### **Nimlgen** [[00:54:49](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3289)]
I think it's good. I haven't seen any issues with the box since the reinstallation. I mean PCI errors.

##### **Geohot** [[00:55:04](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3304)]
I think we've sold three of them too. Got to make sure these are good. Have you seen any PCI errors?

##### **Nimlgen** [[00:55:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3315)]
No. Since the reinstallation of the box, I haven't seen any.

##### **Geohot** [[00:55:21](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3321)]
Actually zero? We should check that, stress that, because if there's any AERs, there's a lot we can do. That one uses the OCP slot, connected to a GPU. We can buy shorter MCIO cables. If there's any way you can get even correctable AERs, let me know, and we'll improve that.

##### **Nimlgen** [[00:55:43](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3343)]
I'll grep for that.

##### **Geohot** [[00:55:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3346)]
We should do that with a lot of people. [Some words unclear.]

##### **Nimlgen** [[00:56:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3360)]
I'll also look into this FLR thing with VFIO.

##### **Geohot** [[00:56:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3366)]
This has been a problem forever. It seems like it's been a thing forever. Every time it FLRs when the GPU is not responding... [trails off].

##### **Chenyu** [[00:56:58](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3418)]
Anything else?

##### **Nimlgen** [[00:57:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3422)]
Also, structs are gone. They're not gone; they're gone for the internal functions.

##### **Geohot** [[00:57:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3430)]
Wonderful. I was happy not to see lots of structs in the emulator. I agree we need it for that purpose.

##### **Chenyu** [[00:57:25](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3445)]
Next, CI machines.

##### **Chrism** [[00:57:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3447)]
The big change is USB GPU is no longer on Comma. It's been a little flaky. I'm hoping a lot of the issues are fixed now that I did a whole bunch of work.

##### **Chrism** [[00:57:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3466)]
One frustrating thing was I had to blacklist xHCI. Since it's compiled into the tinyOS kernel, we have to blacklist it as a kernel argument. When you plug a little console into the computer, the keyboard doesn't work. It doesn't even work over the BMC. It seems to cause a lot of issues if the host kernel's xHCI is allowed to register. For now, I guess you can go find a PS/2 keyboard.

##### **Geohot** [[00:58:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3508)]
There's no PS/2 ports on the computer. Do you have separate cards for the USB?

##### **Chrism** [[00:58:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3518)]
Yeah.

##### **Geohot** [[00:58:42](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3522)]
You can't just blacklist that PCI device? You have to blacklist xHCI entirely?

##### **Chrism** [[00:58:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3527)]
The reason you can't is because it's compiled into the kernel. If it was a module, you could, but we don't even want it to be a module because we need to boot from a USB drive. On these computers we don't, but generically we probably don't want it to be a module.

##### **Geohot** [[00:59:03](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3543)]
Instead of blacklisting xHCI, can't you blacklist the PCI device?

##### **Chrism** [[00:59:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3550)]
No.

##### **Geohot** [[00:59:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3553)]
I'm sure you can.

##### **Chrism** [[00:59:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3557)]
I can look harder, but I'm pretty sure this is not possible if the driver is compiled into the kernel.

##### **Geohot** [[00:59:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3569)]
I'm almost sure there is. You have multiple things that bind to the xHCI device, right? The internal USB hub as well as these cards. It might involve a two-line kernel patch, but there has to be a way.

##### **Chrism** [[00:59:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3587)]
Of course you could do it with a kernel patch.

##### **Geohot** [[00:59:51](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3591)]
There's really no way to say, "Don't bind to these cards"?

##### **Chrism** [[00:59:57](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3597)]
As far as I'm aware, this isn't possible. Astra agrees with me, but I can look into it more.

##### **Geohot** [[01:00:04](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3604)]
If Astra agrees with you, I'm probably wrong, but I'm shocked this isn't a feature.

##### **Chrism** [[01:00:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3610)]
I was surprised too. It seems like the sort of thing that should be allowed. The canonical fix is to make it a module, and in your initramfs, say, "Don't load it for these." But you can't do that if you want to boot from a USB drive.

##### **Geohot** [[01:00:34](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3634)]
xHCI is USB3. Could you load a USB2 driver?

##### **Chrism** [[01:00:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3640)]
I don't know about that. Maybe.

##### **Geohot** [[01:00:44](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3644)]
It's annoying if a keyboard and BMC don't work.

##### **Chrism** [[01:00:48](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3648)]
It is definitely annoying.

##### **Geohot** [[01:00:54](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3654)]
The BMC is on USB?

##### **Chrism** [[01:00:57](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3657)]
Apparently.

##### **Chrism** [[01:01:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3660)]
You have to mash E while the computer is booting so you can delete the blacklist from the GRUB config. I should probably set up GRUB to not go immediately on those computers, at least give you a second to press E. Those are up and hopefully more stable now. I'll keep looking into it if not.

##### **Chrism** [[01:01:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3684)]
I was hoping to get MI300s, sorry, MI350s, MI350Ps to be clear, in Chestnut, but that hasn't worked. I burnt a lot of time trying to get that to work, and it never did.

##### **Geohot** [[01:01:44](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3704)]
MI350Ps can go in a closet and not be used. I don't really care about them.

##### **Chrism** [[01:01:48](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3708)]
Especially considering we're running out of space and power.

##### **Geohot** [[01:01:54](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3714)]
Low priority.

##### **Chrism** [[01:02:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3720)]
Those computers don't draw all that much power, so my plan was to double them up on some red machines on the left side. If you look at the PDU map, or stats.tinygrad.win, you'll see on PDU0, section B, tiny-n1 and r9 are both plugged in there. It looks like it should be fine. If we run into issues, we can power-limit the AMD GPUs.

##### **Chrism** [[01:02:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3767)]
If you look in the history on stats.tinygrad.win, it draws enough power that if all the groups simultaneously drew that much, we'd trip the PDU breaker. As long as we don't do that, we'll be okay.

##### **Geohot** [[01:03:04](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3784)]
We can put r6 on the tiny-n2 one. That was the idea.

##### **Chrism** [[01:03:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3790)]
The other issue is three provisioning ports are taken up by tiny-s1, s2, and s3, but that F slot on PDU1 is completely available now. We can move two of them there, maybe three.

##### **Geohot** [[01:03:34](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3814)]
We're getting another Kimi box and a whale box, and they definitely use power. I'll go to tinygrad chat right now and send some stuff to GLM Flash, and you'll see the power rise.

##### **Chrism** [[01:03:56](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3836)]
I would believe it. We got to figure out what we're going to do about that. Do we really need all the red boxes? They use a lot of power.

##### **Geohot** [[01:04:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3848)]
I want them. That's what's going to serve free inference to everybody.

##### **Chrism** [[01:04:18](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3858)]
They also take a lot of space.

##### **Geohot** [[01:04:23](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3863)]
What's the alternative?

##### **Chrism** [[01:04:33](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3873)]
I don't know. Once we switch the Turins to 5060s, they'll use a lot less power. They're still 3080s right now. We can probably put them all on one PDU group instead of splitting them between two. That frees up another. Still probably not enough... Which one's the whale? The one with 14 GPUs?

##### **Geohot** [[01:05:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3900)]
The whale has 14 GPUs.

##### **Chrism** [[01:05:03](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3903)]
That one's going to be tricky. I don't even know where that's going to go. It's going on the ground. I really don't want to put that on the top shelf.

##### **Geohot** [[01:05:18](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3918)]
We'll have four of the other boxes. Is the whale being built? Would it make you happy to cancel? If it's already being built...

##### **Chrism** [[01:05:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3927)]
The whale is almost entirely built. They're experiencing some issues.

##### **Geohot** [[01:05:32](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3932)]
The BIOS doesn't want to POST. When they take out two GPUs, it POSTs. For reference, the whale has fourteen R9700s and is going to be able to run DeepSeek Flash and full GLM.

##### **Chrism** [[01:06:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3960)]
Other stuff: two of the fans failed in there. I got to figure out something about the fans.

##### **Geohot** [[01:06:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3968)]
The big fans?

##### **Chrism** [[01:06:10](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3970)]
Yeah.

##### **Geohot** [[01:06:11](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3971)]
They're terrible. They don't seem rated for continuous usage, and I don't know how to buy ones on Amazon that are.

##### **Chrism** [[01:06:21](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3981)]
My theory was maybe if we bumped up the debounce time, maybe it'd be better, if we didn't turn them on and off so often.

##### **Geohot** [[01:06:37](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=3997)]
I was looking over the controller logs, and it barely turns on and off. They're basically always on.

##### **Chrism** [[01:06:44](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4004)]
Then maybe that doesn't make sense.

##### **Geohot** [[01:06:46](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4006)]
Maybe we should try a different brand.

##### **Chrism** [[01:06:54](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4014)]
The other stuff is VMs. I've been using them, and I've felt like they're pretty useful. I have them print useful information about how to use them now, and that you can run shutdown rather than complicated delete commands.

##### **Geohot** [[01:07:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4037)]
If I run shutdown, it's deleted now?

##### **Chrism** [[01:07:20](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4040)]
Yeah.

##### **Geohot** [[01:07:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4044)]
What if I run reboot?

##### **Chrism** [[01:07:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4047)]
It won't come back.

##### **Geohot** [[01:07:33](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4053)]
And I lose my drive?

##### **Chrism** [[01:07:35](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4055)]
Yeah.

##### **Geohot** [[01:07:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4060)]
It's a little brutal.

##### **Chrism** [[01:07:43](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4063)]
Why are you rebooting it? It's a VM. Just don't do that.

##### **Geohot** [[01:07:50](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4070)]
My agent rebooted.

##### **Chrism** [[01:07:54](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4074)]
It should have known better. I don't know.

##### **Geohot** [[01:07:58](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4078)]
That seems pretty crazy to me, that rebooting deletes your drive. That's very unexpected.

##### **Chrism** [[01:08:07](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4087)]
I can print a warning.

##### **Geohot** [[01:08:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4093)]
This is an odd thing to do.

##### **Chrism** [[01:08:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4097)]
It requires me to make changes to the image.

##### **Geohot** [[01:08:20](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4100)]
To reboot the computer?

##### **Chrism** [[01:08:22](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4102)]
Yeah. Why are you rebooting?

##### **Geohot** [[01:08:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4109)]
I'm okay with shutting down removing your VM reservation, but it shouldn't remove your storage. No cloud...

##### **Chrism** [[01:08:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4118)]
Sure. Actually, it doesn't remove your storage. The next time you boot, it'll get wiped, and there's no way to access it. But the storage isn't actually deleted. I can add a way to access it.

##### **Geohot** [[01:08:53](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4133)]
I don't care if it shuts down your reservation. In many ways, that's better. But no cloud provider in the world deletes my drive when I shut the machine down.

##### **Chrism** [[01:09:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4146)]
If we don't want to do that, we're already overprovisioned on storage. We need a place to store all this data.

##### **Geohot** [[01:09:19](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4159)]
How much do you need?

##### **Chrism** [[01:09:22](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4162)]
It depends on how frequently people want to do this. Do we want to enable it by default? How much crap are people lugging around in these VMs?

##### **Geohot** [[01:09:31](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4171)]
We could throw some RAID cards in the Turin machines.

##### **Chrism** [[01:09:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4176)]
You store stuff on the Turin machines, and if you shut down a different machine, it exports to that drive?

##### **Geohot** [[01:09:48](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4188)]
Yeah. Where are the VM storage... [trails off].

##### **Chrism** [[01:09:54](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4194)]
This is probably possible, but it sounds a little complicated.

##### **Geohot** [[01:09:57](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4197)]
It definitely involves some planning, but think about extending this to be a generic cloud provider. One of our business models with the MI300s is going to be renting out VMs with them.

##### **Chrism** [[01:10:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4217)]
Sure.

##### **Geohot** [[01:10:20](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4220)]
We have to have the bare minimum of being a cloud provider.

##### **Chrism** [[01:10:27](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4227)]
What if you can suspend your VM, and that's different? Suspend means, "I want to get it back," and you do something special that says suspend, because then we know whether we need to keep your hard drive around.

##### **Geohot** [[01:10:45](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4245)]
If you power off, can it suspend by default and clean up the drive if it hasn't been accessed in 24 hours?

##### **Chrism** [[01:11:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4260)]
I want to do whatever's easy. I'm already way over time on this [unclear].

##### **Chrism** [[01:11:08](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4268)]
The easiest thing is to have something special where you say, "I want to suspend," and then we put your drive somewhere and it's fine.

##### **Geohot** [[01:11:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4277)]
I really don't want the default to be that if my agent types sudo poweroff, I lose my drive.

##### **Chrism** [[01:11:24](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4284)]
Okay, sure.

##### **Geohot** [[01:11:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4288)]
If I type sudo poweroff, I'm totally fine with a cron job cleaning these up after 24 hours of not being used.

##### **Chrism** [[01:11:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4298)]
We'll think about that.

##### **Wozeparrot** [[01:11:43](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4303)]
We also always assume you allocate the same host.

##### **Chrism** [[01:11:47](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4307)]
This is also true. There are a lot of problems. You need to allocate on the same host. Poweroff is fine, but if you suspend and you had GPUs attached, the GPU state is going to be totally different. It defeats the purpose if you're locking the GPUs the entire time.

##### **Geohot** [[01:12:07](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4327)]
I'm not saying I want suspend to actually work as suspend. I'm just saying it doesn't destroy your storage. These storage things should be really tiny too. What we want is some kind of filesystem, and we send it to the other machine.

##### **Chrism** [[01:12:26](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4346)]
That's true.

##### **Geohot** [[01:12:29](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4349)]
On shutdown, can we have something that copies the storage to centralized storage?

##### **Chrism** [[01:12:36](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4356)]
I wouldn't do that in the VM, but certainly we can do this.

##### **Geohot** [[01:12:41](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4361)]
No rush on this. It can delete the storage for now. You're right, there's a lot of complexity I didn't think through.

##### **Chrism** [[01:12:48](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4368)]
I also have to change the image. It wouldn't be that big a change, but the image reformats its drive every time it boots.

##### **Geohot** [[01:12:58](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4378)]
We're going to have to make that change to the image, but it's fine for now.

##### **Chrism** [[01:13:03](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4383)]
The other thing is the router. That's up and running. We have an IP address. I just need to start handing out IPs via the router rather than having Comma hand them out for us.

##### **Geohot** [[01:13:21](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4401)]
Do we have in cloud how many VMs are reserved? We got to get people to start using this. The ultimate test of whether this is good is whether we can migrate people off tinyboxes and onto this.

##### **Chrism** [[01:13:34](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4414)]
If you go to the cloud dashboard, it does say that. It also has an incorrect value for median CI duration. I need to get rid of that or fix it. I had it show the VM count.

##### **Chrism** [[01:13:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4435)]
On the main page at the bottom, it has the cluster status. I should set up alerts so that, like it messages when a CI host goes offline, it also sends a message if one of the cluster members goes offline.

##### **Geohot** [[01:14:20](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4460)]
Let's advertise in tinybox-access and see how many people we can migrate off tinyboxes into this. If we can migrate people off, maybe we can shut that down.

##### **Chrism** [[01:14:34](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4474)]
Right now I added everyone who works here to the admin group, which has access to all the flavors. The idea is you create an invite code corresponding to certain flavors. Everyone who creates an account with that invite code automatically has access to the list of flavors you specified.

##### **Geohot** [[01:15:02](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4502)]
Accounts? Who has accounts?

##### **Chrism** [[01:15:06](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4506)]
You have an account, and I have an account. It associates your SSH key and your...

##### **Geohot** [[01:15:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4513)]
What database is this stored in?

##### **Chrism** [[01:15:17](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4517)]
SQLite.

##### **Geohot** [[01:15:19](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4519)]
We have a SQLite database somewhere that's associating... Got it. We should start advertising to people in here and see if we can get people using it.

##### **Chrism** [[01:15:32](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4532)]
Sounds good. I probably want infrastructure as code for user management too, the same way tinybox-access works now. It's easy to say, "These people haven't logged in in a while; we can remove them."

##### **Chenyu** [[01:16:00](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4560)]
Sounds good. We're over time already. B1, did you want to say something?

##### **Geohot** [[01:16:15](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4575)]
Great. Good work on Kimi. I see you're working on Flash. I think that PR is pretty clean, but it could be cleaning up a bit of stuff.

##### **Chenyu** [[01:16:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4588)]
Sounds good. Any issues for Comma, other than the two elephants to work with?

##### **Chrism** [[01:16:38](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4598)]
Other than the elephants, no. [Name unclear] opened two different PRs, and they both got merged. We can expect a little more of these integration bugs now that we don't test Chestnut with Comma.

##### **Chenyu** [[01:16:55](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4615)]
Speaking of this, is the CI USB GPU still flaky? I've seen four different kinds of error from it.

##### **Chrism** [[01:17:05](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4625)]
It was flaky this morning, and I was hopeful my changes were going to make it better.

##### **Chenyu** [[01:17:13](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4633)]
Sounds good.

##### **Chrism** [[01:17:14](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4634)]
If it continues, I'll keep taking a look. I did see that as well.

##### **Chenyu** [[01:17:28](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4648)]
Sounds good. Anything else for the meeting?

##### **Chrism** [[01:17:37](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4657)]
Nope.

##### **Chenyu** [[01:17:40](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4660)]
That's it for this one. Thank you, everyone. See you next week. Bye-bye.

##### **Geohot** [[01:17:45](https://www.youtube.com/watch?v=B-m2tXbhqWA&t=4665)]
Thanks, everyone. Bye.
