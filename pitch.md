# Lumina — Demo Pitch & Presentation Script

> **Hackathon Pitch & Demo Guide**  
> *Target Duration: 3 Minutes (180 Seconds)*  
> *Goal: Win the Hackathon by proving real clinical impact, technical depth, and safety.*

---

## 🎯 The Hook & Core Narrative (0:00 – 0:30)

**Speaker Setup:**  
"Imagine a child suffering from a rare, undiagnosed condition. For the 300 million people worldwide living with a rare disease, getting a correct diagnosis takes an average of 5 years, 8 different doctors, and dozens of misdiagnoses. Why? Because there are over 7,000 rare diseases, and no human doctor can memorize every gene, symptom, and phenotype pattern.

Meet **Lumina** — a doctor-reviewed rare disease triage and phenotype scoring platform that helps clinicians turn scattered patient evidence into structured diagnoses and specialist referral letters in minutes instead of years."

---

## ⚡ Live Demo Walkthrough (0:30 – 2:30)

### Step 1: Multimodal Intake (0:30 – 1:00)
- **Action on Screen:** Open `/intake` or click a pre-loaded sample case from `/demo` (e.g., Marfan Syndrome or Fabry Disease).
- **Pitch Statement:**  
  "Clinical evidence comes in all shapes: unstructured notes, voice memos, lab reports, genetic VCF files, and patient photos. Lumina ingests all these modalities at once. Watch as our extraction engine automatically identifies candidate Human Phenotype Ontology (HPO) terms from clinical notes and photo evidence."

### Step 2: The Doctor-in-the-Loop Safeguard (1:00 – 1:30)
- **Action on Screen:** Show the interactive phenotype review chips with Accept / Reject buttons.
- **Pitch Statement:**  
  "Here is our core innovation for patient safety: **No unreviewed AI output ever reaches the diagnostic engine.** Lumina presents every extracted term to the clinician. The doctor clicks to accept true phenotypes and reject false ones. Rejected terms are strictly excluded from scoring. AI suggests, but the doctor decides."

### Step 3: Differential Diagnosis & Explainability (1:30 – 2:00)
- **Action on Screen:** Click 'Run Scoring' and navigate to the doctor-facing Results page.
- **Pitch Statement:**  
  "Using only the doctor-approved phenotype profile and genetic variant data, Lumina scores the entire Orphanet knowledge base in real time. Notice that Lumina doesn’t just output a single prediction. It ranks top candidate diseases using Information Content weighted similarity metrics, while showing *why* — detailing matched symptoms, missing findings, and distinguishing features."

### Step 4: Patient-Safe Referral Generation (2:00 – 2:30)
- **Action on Screen:** Click 'Generate Referral Letter' and switch to the Patient Dashboard view.
- **Pitch Statement:**  
  "Finally, Lumina generates a polished, single-page specialist referral letter that the doctor can edit and sign. Crucially, Lumina protects patient wellbeing: patients receive a clear summary and approved referral letter on their dashboard, without exposing raw technical confidence scores that could cause unnecessary panic."

---

## 🚀 Technical Architecture & Impact Summary (2:30 – 3:00)

**Closing Pitch Statement:**  
"Under the hood, Lumina combines Next.js 16, a FastAPI microservice backend, SQLModel ontologies for Orphanet and HPO knowledge graphs, and custom Python similarity rankers. Lumina isn't a speculative wrapper — it is a production-ready clinical decision-support prototype that bridges patient intake and specialist care. 

Thank you, and we welcome your questions!"

---

## ❓ Judge FAQ & Winning Answers

1. **How do you handle AI hallucinations in medical diagnosis?**  
   *Answer:* Lumina strictly enforces a doctor-in-the-loop pipeline. AI findings are presented as pending proposals. Unapproved or rejected terms are completely filtered out before our deterministic ontology similarity engine runs.

2. **Is this using a generic LLM to diagnose patients?**  
   *Answer:* No. The diagnosis engine is a deterministic ranking algorithm (`ScoringIndex`) using HPO graph information content, Jaccard and Lin semantic distance, and ClinVar genetic variant weightings. AI is only used to extract draft phenotype candidates from raw text and images.

3. **How does Lumina protect patient privacy and mental health?**  
   *Answer:* Raw differential rankings and confidence tables are restricted to the clinician interface. Patients receive only doctor-reviewed referral letters and clear summary notes released explicitly by their treating physician.
