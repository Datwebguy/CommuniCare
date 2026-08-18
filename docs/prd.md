# CommuniCare, Product Requirements Document

## Purpose

CommuniCare turns everyday caregiver messages into simple words and high contrast picture symbol boards, so caregivers can communicate more easily with people who are nonverbal or have limited speech. It is being built for the All Things Agentic Hackathon by Google, entered under the Taskmaster track, with a submission deadline of August 31, 2026, at 5:00 PM PDT.

## Problem Statement

Caregivers who support nonverbal or limited speech individuals repeatedly do the same mental work by hand: simplifying language, choosing appropriate picture symbols, and assembling a usable communication board, every time they need to say something. This happens throughout the day, is mentally taxing, and slows down real caregiving moments when speed and clarity matter most. Existing AAC tools generally require the caregiver to manually build boards rather than generating them automatically from natural messages.

## Goal

Remove the manual translation step entirely. A caregiver enters or speaks a normal message, and CommuniCare autonomously produces a ready to use, high contrast picture symbol board, without the caregiver needing to build it by hand, and the board improves over time as it learns the preferences of a specific care recipient.

## Target User

Primary user is the caregiver, whether a family member, home health aide, or care facility staff, who needs a fast way to communicate with someone who is nonverbal or has limited speech. Secondary beneficiary is the care recipient, who receives clearer, more consistent, personalized communication support.

## Core User Story

As a caregiver, when I type or speak a message I need to communicate, I want the system to automatically simplify it and turn it into a picture symbol board I can show the care recipient immediately, without me having to manually pick words or symbols myself.

## Scope for the Hackathon Build

In scope: message input, text simplification, symbol selection and mapping, board assembly, delivery of the finished board, and a basic per care recipient memory of preferred vocabulary and symbols that improves output over repeated use.

Out of scope for this build: multi language support beyond English, a native mobile app binary (PWA/Responsive Web implemented), and live production enterprise SSO.

## Functional Requirements

The system accepts a caregiver message as input, either typed text or a short structured note.
The system uses Gemini 3.5 / 2.5 Flash to simplify the message into short, plain language appropriate for a picture based board.
The system uses Gemini 3.5 / 2.5 Flash to reason about which concepts in the simplified message map to available picture symbols.
The system assembles a visual board from the selected symbols in a clear, high contrast layout.
The system delivers the finished board back to the caregiver, ready to show the care recipient.
The system stores a profile per care recipient in Firestore, tracking preferred vocabulary and which symbols have worked well before, and uses that profile to influence future boards for the same care recipient.

## Non Functional Requirements

The board must be genuinely high contrast and simple enough to be usable by someone with limited visual or cognitive processing capacity, this is a real accessibility requirement, not just a style preference.
The pipeline should run end to end without requiring the caregiver to manually intervene at each step, since the hackathon explicitly rewards autonomous action over simple chat.
Picture symbols must come from an open license source, such as ARASAAC or Mulberry Symbols, or be generated directly, never pulled from generic web image search, due to copyright risk in a public hackathon submission.
The system should be deployed on Cloud Run so its operation can be demonstrated and verified during judging.
