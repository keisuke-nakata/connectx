/**
 * This module was automatically generated by `ts-interface-builder`
 */
import * as t from "ts-interface-checker";
// tslint:disable:object-literal-key-quotes

export const Node = t.iface([], {
  "id": "number",
  "repr": "string",
  "isTerminal": "boolean",
  "score": t.union("number", "null"),
  "property": "object",
  "parentEdge": t.union(t.iface([], {
    "turn": t.union(t.lit("player"), t.lit("opponent")),
    "property": "object",
  }), "null"),
  "children": t.array("Node"),
});

const exportedTypeSuite: t.ITypeSuite = {
  Node,
};
export default exportedTypeSuite;