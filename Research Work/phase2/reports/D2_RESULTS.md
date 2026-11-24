# Dataset 2 — English Ham / Spam / Smishing (Secondary)

**Separate experiment.** These scores are not comparable with D1 and must not be pooled or mapped.

## Data and split

5,971 records (ham 4,844 / spam 489 / smishing 638). 37 conflicting spam↔smishing groups (76 records) excluded. 70/15/15 grouped-stratified split: train **4,127**, validation **885**, test **883** (ham 726 / spam 67 / smishing 90). Zero group/normalised overlap.

## Test results

| model | features | C | accuracy | macro-F1 | Ham F1 | Spam F1 | Smishing F1 |
|---|---|---|---|---|---|---|---|
| linear_svm | char_2_4 | 0.5 | 0.9638 | 0.8825 | 0.9904 | 0.7761 | 0.8810 |
| logreg | char_2_4 | 1.0 | 0.9638 | 0.8877 | 0.9897 | 0.8029 | 0.8706 |

**Selected model:** logreg (validation macro-F1). Confusion matrix:

| true \ pred | ham | spam | smishing |
|---|---|---|---|
| ham | 722 | 0 | 4 |
| spam | 10 | 55 | 2 |
| smishing | 1 | 15 | 74 |

Per class (selected model):

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| ham | 0.9850 | 0.9945 | 0.9897 | 726 |
| spam | 0.7857 | 0.8209 | 0.8029 | 67 |
| smishing | 0.9250 | 0.8222 | 0.8706 | 90 |

- Smishing recall 82.22%; spam F1 0.8029.
- Main confusions: smishing→spam (15), spam→ham (10), ham→smishing (4), spam→smishing (2), smishing→ham (1).
- **Spam is the weakest class**; the spam/smishing boundary is inherently noisy (37 conflicting groups in the source).

## Error examples

| record | line | true | pred | margin | message (truncated) |
|---|---|---|---|---|---|
| D2-04565 | 4567 | smishing | spam | 0.9250 | Txt: CALL to No: 86888 & claim your reward of 3 hours talk time to use from your phone now! Subscribe6GBP/mnth inc 3hrs 16 stop?txtStop www. |
| D2-00768 | 770 | spam | ham | 0.9216 | Do you ever notice that when you're driving, anyone going slower than you is an idiot and everyone driving faster than you is a maniac? |
| D2-04483 | 4485 | smishing | spam | 0.9059 | U are subscribed to the best Mobile Content Service in the UK for £3 per ten days until you send STOP to 83435. Helpline 08706091795. |
| D2-05181 | 5183 | smishing | spam | 0.8286 | 	FreeMsg Today's the day if you are ready! I'm  & live in your town. I love sex fun & games! Netcollex Ltd 08700621170150p per msg reply Sto |
| D2-03809 | 3811 | smishing | spam | 0.8082 | For ur chance to win a £250 wkly shopping spree TXT: SHOP to 80878. T's&C's  custcare 08715705022, 1x150p/wk |
| D2-03623 | 3625 | spam | ham | 0.7924 | How come it takes so little time for a child who is afraid of the dark to become a teenager who wants to stay out all night? |
| D2-02728 | 2730 | smishing | spam | 0.7821 | Text & meet someone sexy today. U can find a date or even flirt its up to U. Join 4 just 10p. REPLY with NAME & AGE eg Sam 25. 18 -msg recd@ |
| D2-04011 | 4013 | spam | ham | 0.7260 | Would you like to see my XXX pics ...they were nearly banned in the uk! |
| D2-01314 | 1316 | smishing | spam | 0.7192 | 500 New Mobiles from 2004, MUST GO! Txt: NOKIA to No: 89545 & collect yours today!From ONLY £1 www.4-tc.biz 2optout 087187262701.50gbp/mtmsg |
| D2-02362 | 2364 | spam | ham | 0.7121 | This message is brought to you by GMW Ltd. and is not connected to the |
| D2-04596 | 4598 | smishing | spam | 0.7020 | BangBabes Ur order is on the way. U SHOULD receive a Service Msg 2 download UR content. If U do not, GoTo wap. bangb. tv on UR mobile intern |
| D2-03261 | 3263 | smishing | spam | 0.6754 | Natalja (25/F) is inviting you to be her friend.  See her: www.SMS.ac/u/nat27081980 STOP? Send STOP FRND to 62468 |

## Caveat

D2 is English/Latin-script only (0 Indic records) and its ham/spam portion derives from UCI. Near-ceiling Ham performance is expected; the useful signal is the spam/smishing boundary. No claim about Malayalam smishing follows from this experiment.
