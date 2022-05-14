import * as go from 'gojs';
import { ReactDiagram, DiagramProps } from 'gojs-react';
import { useAppSelector } from '../../app/hooks';
import { Node } from './node';
import styles from './Tree.module.css';
import { selectData } from './treeSlice';

const GOJSSTYLES = {
  Diagram: {
    initialAutoScale: go.Diagram.UniformToFill,
    layout: new go.TreeLayout({ angle: 90, layerSpacing: 50 }),
    model: new go.TreeModel({
      isReadOnly: true, // don't allow the user to delete or copy nodes
    }),
  },
  Node: {
    Table: {
      Header0: { row: 0 },
      Header1: { row: 1, margin: new go.Margin(0, 24, 0, 2) },  // 展開ボタンのための余裕しろ
      ExpanderButton: { row: 1, alignment: go.Spot.TopRight },
      Content: { row: 2, font: "16px monospace" },
    },
  },
  Link: {
    Link: { routing: go.Link.Orthogonal, selectable: false, corner: 10 },
    TextBlock: { segmentIndex: -2, background: "white" },
  },
};

const initDiagram = () => {
  const diagram = new go.Diagram(GOJSSTYLES.Diagram);

  diagram.nodeTemplate = new go.Node("Vertical").bind("isTreeExpanded", "isRational")
    .add(new go.Panel("Table")
      .add(new go.TextBlock(GOJSSTYLES.Node.Table.Header0)
        .bind("text", "isTerminal", (isTerminal) => "terminal: " + isTerminal)
        .bind("stroke", "isTerminal", (isTerminal) => isTerminal ? "black" : "gray"))
      .add(new go.TextBlock(GOJSSTYLES.Node.Table.Header1)
        .bind("text", "properties", (obj) => JSON.stringify(obj, null, "__")))
      .add(go.GraphObject.make("PanelExpanderButton", "CONTENT", GOJSSTYLES.Node.Table.ExpanderButton))
      .add(new go.TextBlock({ name: "CONTENT", ...GOJSSTYLES.Node.Table.Content})
        .bind("text", "repr")))
    .add(go.GraphObject.make("TreeExpanderButton"));

  diagram.linkTemplate = new go.Link(GOJSSTYLES.Link.Link)
    .add(new go.Shape()
      .bind("stroke", "edgeColor")
      .bind("strokeWidth", "edgeIsRational", (edgeIsRational) => edgeIsRational ? 5 : 1))
    .add(new go.TextBlock(GOJSSTYLES.Link.TextBlock)
      .bind("text", "edgeRepr"));

  return diagram;
};

const nodeToArray = (node: Node, parentId: string | null) => {
  const thisParentEdge = node.parentEdge ? {
    parent: parentId,
    edgeRepr: node.parentEdge.repr,
    edgeTurn: node.parentEdge.turn,
    edgeColor: node.parentEdge.turn === "player" ? "DeepSkyBlue" : "red",
    edgeIsRational: node.parentEdge.isRational,
    edgeProperies: node.parentEdge.properties,
  } : {};
  const thisNode: DiagramProps["nodeDataArray"] = [{
    key: node.id,
    repr: node.repr,
    isTerminal: node.isTerminal,
    isRational: node.isRational,
    properties: node.properties,
    ...thisParentEdge,
  }];
  if (node.children.length > 0) {
    const children = node.children.flatMap(child => nodeToArray(child, node.id));
    thisNode.push(...children);
  }
  return thisNode;
};

export const TreeViz = () => {
  const rootNode = useAppSelector(selectData);
  const nodeDataArray = nodeToArray(rootNode, null);

  return (
    <ReactDiagram
      initDiagram={initDiagram}
      divClassName={styles.diagramComponent}
      nodeDataArray={nodeDataArray}
    />
  );
};
