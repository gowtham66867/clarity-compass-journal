import { after, afterEach, before, describe, test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

import {
  assertFails,
  assertSucceeds,
  initializeTestEnvironment,
} from "@firebase/rules-unit-testing";
import {
  collection,
  deleteDoc,
  doc,
  getDoc,
  getDocs,
  setDoc,
} from "firebase/firestore";

const PROJECT_ID = "demo-clarity-compass";
let testEnv;

before(async () => {
  const rules = await readFile(new URL("../firestore.rules", import.meta.url), "utf8");
  testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: { rules },
  });
});

afterEach(async () => {
  await testEnv.clearFirestore();
});

after(async () => {
  await testEnv.cleanup();
});

function interaction(database, owner, interaction = "entry-1") {
  return doc(database, "users", owner, "interactions", interaction);
}

describe("Firestore owner isolation", () => {
  test("authenticated users can create, read, update, and delete their own interaction", async () => {
    const alice = testEnv.authenticatedContext("alice").firestore();
    const ref = interaction(alice, "alice");

    await assertSucceeds(setDoc(ref, { prompt: "Synthetic test", mode: "clarity" }));
    const snapshot = await assertSucceeds(getDoc(ref));
    assert.equal(snapshot.data().mode, "clarity");
    await assertSucceeds(setDoc(ref, { mode: "decision" }, { merge: true }));
    await assertSucceeds(deleteDoc(ref));
  });

  test("authenticated users can list only their own interaction collection", async () => {
    const alice = testEnv.authenticatedContext("alice").firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await setDoc(interaction(context.firestore(), "alice"), { owner: "alice" });
      await setDoc(interaction(context.firestore(), "bob"), { owner: "bob" });
    });

    const snapshot = await assertSucceeds(
      getDocs(collection(alice, "users", "alice", "interactions")),
    );
    assert.equal(snapshot.size, 1);
    assert.equal(snapshot.docs[0].data().owner, "alice");
  });

  test("one user cannot read, list, create, update, or delete another user's data", async () => {
    const alice = testEnv.authenticatedContext("alice").firestore();
    const bobRefFromAlice = interaction(alice, "bob");
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await setDoc(interaction(context.firestore(), "bob"), { owner: "bob" });
    });

    await assertFails(getDoc(bobRefFromAlice));
    await assertFails(getDocs(collection(alice, "users", "bob", "interactions")));
    await assertFails(setDoc(bobRefFromAlice, { owner: "alice" }));
    await assertFails(setDoc(bobRefFromAlice, { changed: true }, { merge: true }));
    await assertFails(deleteDoc(bobRefFromAlice));
  });

  test("unauthenticated clients cannot read, list, create, update, or delete interactions", async () => {
    const guest = testEnv.unauthenticatedContext().firestore();
    const ref = interaction(guest, "alice");
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await setDoc(interaction(context.firestore(), "alice"), { owner: "alice" });
    });

    await assertFails(getDoc(ref));
    await assertFails(getDocs(collection(guest, "users", "alice", "interactions")));
    await assertFails(setDoc(ref, { owner: "guest" }));
    await assertFails(setDoc(ref, { changed: true }, { merge: true }));
    await assertFails(deleteDoc(ref));
  });

  test("all documents outside the interaction path are denied", async () => {
    const alice = testEnv.authenticatedContext("alice").firestore();

    await assertFails(setDoc(doc(alice, "users", "alice"), { role: "admin" }));
    await assertFails(setDoc(doc(alice, "admin", "settings"), { enabled: true }));
    await assertFails(getDoc(doc(alice, "admin", "settings")));
  });
});
