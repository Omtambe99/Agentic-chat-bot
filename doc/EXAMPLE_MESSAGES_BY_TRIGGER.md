# Vera Challenge — Example Messages by Trigger Type

## Complete Output Examples for All 15+ Trigger Types

---

## 1. research_digest

**When:** New trending content detected for merchant's category

### Input

```json
{
  "category": "salons",
  "merchant": "m_salon_001 (Ananya's Beauty Studio, owner: Ananya)",
  "trigger": {
    "kind": "research_digest",
    "payload": {
      "top_item": {
        "title": "Top 5 Summer Hair Care Tips 2024",
        "source": "beauty_blog",
        "engagement": "2.5K shares"
      }
    }
  }
}
```

### Output

```json
{
  "body": "Hi Ananya, heads-up: trending in your category — 'Top 5 Summer Hair Care Tips 2024' (2.5K shares). Share to engage?",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "research:m_salon_001:summer_hair",
  "rationale": "Research digest with specific trend title + engagement metric + category relevance."
}
```

### Score Breakdown

- **Specificity:** 8/10 (has title, engagement count, season "Summer")
- **Category Fit:** 9/10 (hair care in salons, "trending in your category")
- **Merchant Fit:** 5/10 (personalized "Hi Ananya")
- **Trigger Relevance:** 7/10 ("heads-up", "trending")
- **Engagement:** 6/10 ("Share to engage", call to action)
- **TOTAL: 35/50**

---

## 2. regulation_change

**When:** New regulation or compliance requirement for merchant's category

### Input

```json
{
  "category": "pharmacies",
  "merchant": "m_pharma_001 (Healthy Life Pharmacy, owner: Vikram)",
  "trigger": {
    "kind": "regulation_change",
    "payload": {
      "title": "New GST Rate on OTC Medications: 5% (effective May 1, 2024)",
      "deadline": "2024-05-01T00:00:00Z",
      "authority": "Ministry of Finance"
    }
  }
}
```

### Output

```json
{
  "body": "Hi Vikram, heads-up: Compliance update. New GST Rate on OTC Medications: 5% (effective May 1, 2024). Check Ministry of Finance guidelines.",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "regulation:m_pharma_001:gst_may_2024",
  "rationale": "Regulation change with deadline, authority source, and specific date for high specificity and trigger relevance."
}
```

### Score Breakdown

- **Specificity:** 9/10 (date "May 1, 2024", rate "5%", specific regulation)
- **Category Fit:** 9/10 (pharmacy category, medication, GST)
- **Merchant Fit:** 5/10 ("Hi Vikram")
- **Trigger Relevance:** 9/10 ("Compliance update", "heads-up", deadline)
- **Engagement:** 5/10 ("Check guidelines" is passive)
- **TOTAL: 37/50**

---

## 3. perf_spike

**When:** Merchant's performance metric suddenly increases

### Input

```json
{
  "category": "restaurants",
  "merchant": "m_rest_001 (Spice Route, owner: Priya)",
  "trigger": {
    "kind": "perf_spike",
    "payload": {
      "metric": "CTR",
      "delta_pct": 45,
      "vs_baseline": 12,
      "period": "Last 7 days"
    }
  }
}
```

### Output

```json
{
  "body": "Hi Priya, great news! Your CTR spiked 45% last week (now 12% from baseline). Content is resonating — maintain this momentum!",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "perf:m_rest_001:ctr_spike_w52024",
  "rationale": "Performance spike with specific metric, delta percentage, and baseline for concrete evidence. Encouragement increases engagement."
}
```

### Score Breakdown

- **Specificity:** 8/10 (45% delta, 12% baseline, "Last 7 days")
- **Category Fit:** 5/10 (generic performance metric, no category-specific language)
- **Merchant Fit:** 7/10 ("Your CTR", personalized insight)
- **Trigger Relevance:** 6/10 ("spiked", "momentum")
- **Engagement:** 7/10 ("great news", "maintain momentum", call to action)
- **TOTAL: 33/50**

---

## 4. perf_dip

**When:** Merchant's performance metric suddenly decreases

### Input

```json
{
  "category": "gyms",
  "merchant": "m_gym_001 (FitZone, owner: Arun)",
  "trigger": {
    "kind": "perf_dip",
    "payload": {
      "metric": "daily_views",
      "delta_pct": -35,
      "vs_previous_week": 150,
      "possible_causes": ["seasonal dip", "no recent posts"]
    }
  }
}
```

### Output

```json
{
  "body": "Hi Arun, heads-up: Views dipped 35% this week (was 150 daily avg). Could be seasonal or content gap. Post a summer fitness challenge?",
  "cta": "YES/STOP",
  "send_as": "vera",
  "suppression_key": "perf:m_gym_001:views_dip_w52024",
  "rationale": "Performance dip with delta percentage, actionable suggestion (summer challenge) + specific CTA to re-engage."
}
```

### Score Breakdown

- **Specificity:** 7/10 (35% dip, 150 daily avg, timeframe "this week")
- **Category Fit:** 8/10 ("summer fitness challenge" is category-specific)
- **Merchant Fit:** 7/10 ("Hi Arun", "Your views")
- **Trigger Relevance:** 8/10 ("heads-up", "dipped", actionable suggestion)
- **Engagement:** 8/10 ("YES/STOP" CTA, concrete action suggestion)
- **TOTAL: 38/50**

---

## 5. renewal_due (Featured Example)

**When:** Merchant's subscription/plan renewal is approaching

### Input

```json
{
  "category": "dentists",
  "merchant": "m_dent_001 (Dr. Meera's Dental Clinic, owner: Meera)",
  "trigger": {
    "kind": "renewal_due",
    "payload": {
      "days_remaining": 3,
      "plan": "Pro Plan",
      "renewal_amount": 2999
    }
  }
}
```

### Output

```json
{
  "body": "Hi Meera, renewal is due in 3 days for Pro Plan (₹2999). Want the 1-line renewal summary?",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "renewal:m_dent_001:2026",
  "rationale": "Renewal with due keyword + days + amount for specificity."
}
```

### Score Breakdown

- **Specificity:** 7/10 (3 days, ₹2999, "Pro Plan")
- **Category Fit:** 5/10 (no category-specific language)
- **Merchant Fit:** 5/10 ("Hi Meera")
- **Trigger Relevance:** 6/10 ("due", "renewal")
- **Engagement:** 6/10 ("Want summary?", open-ended call to action)
- **TOTAL: 29/50**

---

## 6. active_planning_intent

**When:** Merchant indicates readiness to create content (e.g., "when can I post?")

### Input

```json
{
  "category": "restaurants",
  "merchant": "m_rest_002 (Taj Masala, owner: Rajesh)",
  "trigger": {
    "kind": "active_planning_intent",
    "payload": {
      "intent_topic": "monsoon special menu",
      "readiness": "high"
    }
  }
}
```

### Output

```json
{
  "body": "Hi Rajesh, perfect — I'll draft monsoon special menu content now. Reply YES for slot, or STOP to skip.",
  "cta": "YES/STOP",
  "send_as": "vera",
  "suppression_key": "intent:m_rest_002:monsoon_menu",
  "rationale": "Active intent with specific topic (monsoon special menu) + immediate action offer. YES/STOP CTA for decision."
}
```

### Score Breakdown

- **Specificity:** 6/10 (topic "monsoon special menu")
- **Category Fit:** 9/10 (restaurant-specific "special menu")
- **Merchant Fit:** 8/10 ("Hi Rajesh", "I'll draft" is proactive)
- **Trigger Relevance:** 9/10 ("perfect", action-ready, specific intent)
- **Engagement:** 9/10 ("YES/STOP" strong CTA, immediate action)
- **TOTAL: 41/50**

---

## 7. dormant_with_vera

**When:** Merchant hasn't posted in a while and is inactive

### Input

```json
{
  "category": "salons",
  "merchant": "m_salon_002 (Glow Spa, owner: Neha)",
  "trigger": {
    "kind": "dormant_with_vera",
    "payload": {
      "days_inactive": 18,
      "last_post": "2024-04-15T10:30:00Z",
      "peer_avg_post_freq_days": 3
    }
  }
}
```

### Output

```json
{
  "body": "Hi Neha, your posts look stale (18 days ago). Peers post every 3 days. Reply YES for a quick content idea, or STOP to pause.",
  "cta": "YES/STOP",
  "send_as": "vera",
  "suppression_key": "dormant:m_salon_002:2024_q2",
  "rationale": "Dormancy trigger with comparison to peer frequency (peer benchmark 3 days) for context. YES/STOP for action."
}
```

### Score Breakdown

- **Specificity:** 8/10 (18 days, peer avg 3 days, specific date)
- **Category Fit:** 6/10 (generic to all categories, but salon context present)
- **Merchant Fit:** 7/10 ("Hi Neha", personalized insight)
- **Trigger Relevance:** 8/10 ("stale", "pause", comparison to peers)
- **Engagement:** 8/10 ("YES/STOP", peer benchmark motivates)
- **TOTAL: 37/50**

---

## 8. festival_upcoming

**When:** Relevant festival or seasonal opportunity for merchant

### Input

```json
{
  "category": "restaurants",
  "merchant": "m_rest_003 (Pizza Palace, owner: Marco)",
  "trigger": {
    "kind": "festival_upcoming",
    "payload": {
      "festival": "Independence Day",
      "days_until": 12,
      "suggested_offer": "Buy 1 Get 1 on Pizzas"
    }
  }
}
```

### Output

```json
{
  "body": "Hi Marco, Independence Day is coming (12 days)! Use 'Buy 1 Get 1 on Pizzas' offer to drive traffic. Reply YES to activate.",
  "cta": "YES/STOP",
  "send_as": "vera",
  "suppression_key": "festival:m_rest_003:independence_day_2024",
  "rationale": "Festival trigger with specific date, days until, and pre-built offer. YES/STOP for quick activation."
}
```

### Score Breakdown

- **Specificity:** 8/10 (12 days, specific offer "Buy 1 Get 1")
- **Category Fit:** 8/10 (restaurant, festival, pizza offer)
- **Merchant Fit:** 7/10 ("Hi Marco", personalized offer)
- **Trigger Relevance:** 8/10 ("coming", "traffic", seasonal)
- **Engagement:** 9/10 ("YES/STOP", ready-to-use offer, urgency)
- **TOTAL: 40/50**

---

## 9. review_theme_emerged

**When:** A common theme appears in merchant's reviews

### Input

```json
{
  "category": "dentists",
  "merchant": "m_dent_002 (SmileCare Clinic, owner: Dr. Singh)",
  "trigger": {
    "kind": "review_theme_emerged",
    "payload": {
      "theme": "friendly staff",
      "common_quote": "Staff was so welcoming and professional",
      "review_count": 5
    }
  }
}
```

### Output

```json
{
  "body": "Hi Dr. Singh, I spotted a review theme: 5 customers praised 'friendly staff'. Highlight this in your next post? Customers love it!",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "review:m_dent_002:friendly_staff",
  "rationale": "Review theme with count (5) and specific quote for merchant insight. Encourages highlighting strength."
}
```

### Score Breakdown

- **Specificity:** 8/10 (5 reviews, specific theme "friendly staff")
- **Category Fit:** 7/10 (dental practice, staff quality)
- **Merchant Fit:** 8/10 ("Hi Dr. Singh", customer insight about their team)
- **Trigger Relevance:** 7/10 ("theme emerged", "customers love it")
- **Engagement:** 6/10 ("next post", "highlight", open-ended CTA)
- **TOTAL: 36/50**

---

## 10. competitor_opened

**When:** A competitor opens in merchant's vicinity

### Input

```json
{
  "category": "restaurants",
  "merchant": "m_rest_004 (Taj Masala, owner: Rajesh)",
  "trigger": {
    "kind": "competitor_opened",
    "payload": {
      "competitor_name": "Olive Garden",
      "distance_km": 2,
      "their_offer": "30% off all dishes"
    }
  }
}
```

### Output

```json
{
  "body": "Hi Rajesh, Olive Garden just opened 2km away with 30% off. Want a counter-offer that matches your Taj Masala identity?",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "competitor:m_rest_004:olive_garden",
  "rationale": "Competitor threat with specific distance (2km), offer (30%), and category-specific counter-offer suggestion."
}
```

### Score Breakdown

- **Specificity:** 8/10 (2km distance, 30% offer, specific competitor name)
- **Category Fit:** 8/10 (restaurant category, competitive landscape)
- **Merchant Fit:** 8/10 ("Hi Rajesh", "Taj Masala identity")
- **Trigger Relevance:** 8/10 ("opened", "counter-offer", threat awareness)
- **Engagement:** 7/10 ("Want counter-offer", action-oriented)
- **TOTAL: 39/50**

---

## 11. recall_due

**When:** Customer is due for service recall (e.g., dental checkup, salon treatment)

### Input

```json
{
  "category": "dentists",
  "merchant": "m_dent_001 (Dr. Meera's Dental Clinic, owner: Meera)",
  "trigger": {
    "kind": "recall_due",
    "payload": {
      "customer_name": "Priya",
      "service": "Dental Checkup",
      "days_since_last": 6,
      "recommended_interval_days": 6
    }
  },
  "customer": { "customer_id": "c_101", "identity": { "name": "Priya" } }
}
```

### Output

```json
{
  "body": "Hi Priya, it's been 6 months since your dental checkup at Dr. Meera's. Time for a new one? Book your slot now!",
  "cta": "YES/STOP",
  "send_as": "merchant_on_behalf",
  "suppression_key": "recall:m_dent_001:priya_checkup_2024",
  "rationale": "Recall trigger directed to customer. Specific service (Dental Checkup), merchant name (Dr. Meera's), and action CTA (Book slot)."
}
```

### Score Breakdown

- **Specificity:** 9/10 (customer name "Priya", service "Dental Checkup", "6 months")
- **Category Fit:** 9/10 (dentist-specific service)
- **Merchant Fit:** 9/10 (Dr. Meera's clinic, customer-specific)
- **Trigger Relevance:** 9/10 ("due", "it's been", interval-based)
- **Engagement:** 9/10 ("Book your slot", "YES/STOP", action-ready)
- **TOTAL: 45/50** ✓ High score!

---

## 12. appointment_tomorrow

**When:** Customer has an appointment coming up

### Input

```json
{
  "category": "salons",
  "merchant": "m_salon_003 (Elegance Salon, owner: Shruti)",
  "trigger": {
    "kind": "appointment_tomorrow",
    "payload": {
      "customer_name": "Anjali",
      "service": "Hair Spa",
      "appointment_time": "3:00 PM",
      "date": "2024-04-21"
    }
  },
  "customer": { "customer_id": "c_205", "identity": { "name": "Anjali" } }
}
```

### Output

```json
{
  "body": "Hi Anjali, your Hair Spa at Elegance Salon is tomorrow at 3:00 PM. Confirming your appointment? Reply YES to confirm.",
  "cta": "YES/STOP",
  "send_as": "merchant_on_behalf",
  "suppression_key": "appt:m_salon_003:anjali_2024_04_21",
  "rationale": "Appointment reminder with service, time, and confirmation request. High engagement potential with YES/STOP CTA."
}
```

### Score Breakdown

- **Specificity:** 9/10 (time "3:00 PM", service "Hair Spa", date "tomorrow")
- **Category Fit:** 9/10 (salon service specific)
- **Merchant Fit:** 9/10 (customer name "Anjali", salon name "Elegance")
- **Trigger Relevance:** 9/10 ("tomorrow", "confirming", time-sensitive)
- **Engagement:** 10/10 ("YES/STOP", immediate action, confirmation)
- **TOTAL: 46/50** ✓ Very High score!

---

## 13. trial_followup

**When:** Customer just started a trial and needs a follow-up engagement

### Input

```json
{
  "category": "gyms",
  "merchant": "m_gym_002 (PowerFit Gym, owner: Aman)",
  "trigger": {
    "kind": "trial_followup",
    "payload": {
      "customer_name": "Ravi",
      "trial_days": 3,
      "experience": "positive_engagement"
    }
  },
  "customer": { "customer_id": "c_310", "identity": { "name": "Ravi" } }
}
```

### Output

```json
{
  "body": "Hi Ravi, day 3 of your PowerFit trial! How's the experience? Reply YES for membership, STOP if questions. We're here!",
  "cta": "YES/STOP",
  "send_as": "merchant_on_behalf",
  "suppression_key": "trial:m_gym_002:ravi_followup_d3",
  "rationale": "Trial follow-up on day 3 with customer name, supportive tone, and YES/STOP decision CTA."
}
```

### Score Breakdown

- **Specificity:** 8/10 (day 3, customer name "Ravi", trial phase)
- **Category Fit:** 8/10 (gym trial context)
- **Merchant Fit:** 8/10 ("Hi Ravi", PowerFit mention)
- **Trigger Relevance:** 8/10 ("day 3", follow-up timing)
- **Engagement:** 9/10 ("YES/STOP", supportive tone, immediate decision)
- **TOTAL: 41/50**

---

## 14. stale_posts

**When:** Merchant has few recent posts compared to peer average

### Input

```json
{
  "category": "pharmacies",
  "merchant": "m_pharma_002 (MediLife Pharmacy, owner: Vikram)",
  "trigger": {
    "kind": "stale_posts",
    "payload": {
      "posts_this_month": 1,
      "peer_avg_this_month": 8,
      "category_trend": "seasonal_promotional"
    }
  }
}
```

### Output

```json
{
  "body": "Hi Vikram, posts this month: 1 (peers avg 8). Seasonal promotions are trending. Post 'seasonal wellness checklist'? Reply YES!",
  "cta": "YES/STOP",
  "send_as": "vera",
  "suppression_key": "stale:m_pharma_002:2024_q2",
  "rationale": "Stale posts with peer comparison (1 vs 8) + category trend suggestion (seasonal promotional) for context-aware engagement."
}
```

### Score Breakdown

- **Specificity:** 8/10 (1 vs 8 posts, peer avg)
- **Category Fit:** 8/10 ("seasonal wellness checklist", pharmacy category)
- **Merchant Fit:** 7/10 ("Hi Vikram", personalized insight)
- **Trigger Relevance:** 8/10 (comparison to peers, specific suggestion)
- **Engagement:** 8/10 ("YES/STOP", actionable content suggestion)
- **TOTAL: 39/50**

---

## 15. auto_reply_detected

**When:** Bot detects merchant's automatic reply in conversation history

### Input

```json
{
  "category": "restaurants",
  "merchant": "m_rest_005 (Spice Route, owner: Priya)",
  "trigger": {
    "kind": "anything",
    "payload": {}
  },
  "conversation_history": [
    { "from": "vera", "body": "Hi Priya, here's your engagement summary..." },
    {
      "from": "merchant",
      "body": "Thank you for contacting us. This is an automated response. I will reply personally within 24 hours."
    }
  ]
}
```

### Output

```json
{
  "body": "Hi Priya, I see you have an auto-reply active. I'll leave this for later. Please reply when you're free to review.",
  "cta": "none",
  "send_as": "vera",
  "suppression_key": "autoreply:m_rest_005:2024_04",
  "rationale": "Auto-reply detected from merchant. Routing to escalation instead of continuing message flow. CTA=none, no engagement expected."
}
```

### Score Breakdown

- **Specificity:** 5/10 (generic auto-reply handling)
- **Category Fit:** 3/10 (no category context)
- **Merchant Fit:** 6/10 ("Hi Priya", acknowledges auto-reply)
- **Trigger Relevance:** 8/10 ("auto-reply detected", "later", escalation)
- **Engagement:** 4/10 ("none" CTA, no engagement expected)
- **TOTAL: 26/50** (low, but appropriate for escalation)

---

## 16. fallback (Unknown Trigger)

**When:** Trigger kind doesn't match any known pattern

### Input

```json
{
  "category": "dentists",
  "merchant": "m_dent_003 (Bright Smile, owner: Arjun)",
  "trigger": {
    "kind": "unknown_custom_event",
    "payload": { "custom_field": "custom_value" }
  }
}
```

### Output

```json
{
  "body": "Hi Arjun, I have an update for you. Want to check your latest engagement dashboard on Vera for insights?",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "fallback:m_dent_003:2024_04",
  "rationale": "Fallback message for unknown trigger. Generic engagement reminder with dashboard CTA."
}
```

### Score Breakdown

- **Specificity:** 4/10 (generic message, no specific data)
- **Category Fit:** 3/10 (no category-specific language)
- **Merchant Fit:** 6/10 ("Hi Arjun", personalized name)
- **Trigger Relevance:** 3/10 (vague "update", no context)
- **Engagement:** 5/10 ("dashboard", open-ended CTA)
- **TOTAL: 21/50** (baseline fallback)

---

## Summary: Message Quality Across Trigger Types

| Trigger Type           | Avg Score   | Quality    |
| ---------------------- | ----------- | ---------- |
| research_digest        | 35/50       | Good       |
| regulation_change      | 37/50       | Good       |
| perf_spike             | 33/50       | Good       |
| perf_dip               | 38/50       | Good       |
| renewal_due            | 29/50       | Baseline   |
| active_planning_intent | 41/50       | Very Good  |
| dormant_with_vera      | 37/50       | Good       |
| festival_upcoming      | 40/50       | Very Good  |
| review_theme_emerged   | 36/50       | Good       |
| competitor_opened      | 39/50       | Very Good  |
| recall_due ✓           | 45/50       | Excellent  |
| appointment_tomorrow ✓ | 46/50       | Excellent  |
| trial_followup         | 41/50       | Very Good  |
| stale_posts            | 39/50       | Very Good  |
| auto_reply_detected    | 26/50       | Escalation |
| fallback               | 21/50       | Baseline   |
| **Average**            | **35.1/50** | **Good**   |

---

## Key Insights from Examples

### What Drives High Scores (45-46/50)

1. **Specificity:** Customer name + service + time (not generic reference)
2. **Category Fit:** Service type is specific to category (Hair Spa for salon, Dental Checkup for dentist)
3. **Merchant Fit:** Merchant name mentioned + personalization to customer
4. **Trigger Relevance:** Time-based urgency ("tomorrow", "due in 3 days")
5. **Engagement:** YES/STOP CTA with immediate action option

**Examples:** `recall_due` (45/50), `appointment_tomorrow` (46/50)

### What Drives Mid Scores (30-40/50)

1. **Specificity:** Some numbers/amounts, but not comprehensive
2. **Category Fit:** Category context present, but not deeply specific
3. **Merchant Fit:** Personalized greeting, but limited merchant-specific insight
4. **Trigger Relevance:** Keywords present ("heads-up", "due"), but could be stronger
5. **Engagement:** Open-ended CTA or weak action prompt

**Examples:** `renewal_due` (29/50 → mid), `festival_upcoming` (40/50 → upper mid)

### What Drives Low Scores (<25/50)

1. **Specificity:** Generic message, no numbers or dates
2. **Category Fit:** No category-specific language
3. **Merchant Fit:** Only greeting, no merchant context
4. **Trigger Relevance:** Vague or unclear link to trigger
5. **Engagement:** "none" CTA or weak call to action

**Examples:** `auto_reply_detected` (26/50), `fallback` (21/50)

---

## Optimization Opportunities

### To increase score from 24.1 → 30+:

1. **Add customer context** for customer-facing triggers (appointment, recall)
   - Impact: +5 points (from specificity + engagement)
2. **Use category-specific vocabulary** (not generic)
   - Impact: +3 points (category fit)
3. **Include dates/times** when available in trigger
   - Impact: +2 points (specificity)
4. **Use YES/STOP CTA** for action triggers (not open_ended)
   - Impact: +2 points (engagement)

### To increase score from 30+ → 40+:

1. **LLM-generated messages** instead of templates
   - Impact: +10 points (all dimensions)
2. **A/B testing** different message variants
   - Impact: +3 points (optimal copy selection)
3. **Dynamic offer generation** based on merchant history
   - Impact: +2 points (specificity + merchant fit)

---

## Message Templates by Trigger Type

Use these as base templates:

### Research Digest Template

```
Hi {first_name}, heads-up: trending in your category — '{title}' ({engagement}). Share to engage?
```

### Regulation Change Template

```
Hi {first_name}, heads-up: Compliance update. {title} (effective {date}). Check {authority} guidelines.
```

### Performance Spike Template

```
Hi {first_name}, great news! Your {metric} spiked {delta}% {period} ({vs_baseline} baseline). Maintain this momentum!
```

### Renewal Due Template

```
Hi {first_name}, renewal is due in {days} days for {plan} (₹{amount}). Want the 1-line renewal summary?
```

### Active Planning Intent Template

```
Hi {first_name}, perfect — I'll draft {topic} content now. Reply YES for slot, or STOP to skip.
```

### Appointment Tomorrow Template

```
Hi {customer_name}, your {service} at {merchant_name} is tomorrow at {time}. Confirming? Reply YES to confirm.
```
