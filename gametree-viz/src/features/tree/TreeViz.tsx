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
      Header: { row: 0, margin: new go.Margin(0, 24, 0, 2) },  // 展開ボタンのための余裕しろ
      ExpanderButton: { row: 0, alignment: go.Spot.TopRight },
      Content: { row: 1, visible: false },
    },
  },
  Link: {
    Link: { routing: go.Link.Orthogonal, selectable: false, corner: 10 },
    Shape: { strokeWidth: 1 },
    TextBlock: { segmentIndex: -2, background: "white" },
  },
};

const initDiagram = () => {
  const diagram = new go.Diagram(GOJSSTYLES.Diagram);

  diagram.nodeTemplate = new go.Node("Vertical")
    .add(new go.Panel("Table")
      .add(new go.TextBlock(GOJSSTYLES.Node.Table.Header)
        .bind("text", "key"))
      .add(go.GraphObject.make("PanelExpanderButton", "CONTENT", GOJSSTYLES.Node.Table.ExpanderButton))
      .add(new go.TextBlock({ name: "CONTENT", ...GOJSSTYLES.Node.Table.Content})
        .bind("text", "repr")))
    .add(go.GraphObject.make("TreeExpanderButton"));

  diagram.linkTemplate = new go.Link(GOJSSTYLES.Link.Link)
    .add(new go.Shape(GOJSSTYLES.Link.Shape)
      .bind("stroke", "edgeColor"))
    .add(new go.TextBlock(GOJSSTYLES.Link.TextBlock)
      .bind("text", "edgeRepr"));

  return diagram;
};

const nodeToArray = (node: Node, parentId: number | null) => {
  const thisParentEdge = node.parentEdge ? {
    parent: parentId,
    edgeRepr: node.parentEdge.repr,
    edgeTurn: node.parentEdge.turn,
    edgeColor: node.parentEdge.turn === "player" ? "DeepSkyBlue" : "red",
  } : {};
  const thisNode: DiagramProps["nodeDataArray"] = [{
    key: node.id,
    repr: node.repr,
    ...thisParentEdge,
  }];
  if (node.children.length > 0) {
    const children = node.children.flatMap(child => nodeToArray(child, node.id));
    thisNode.push(...children);
  }
  return thisNode
};

export const TreeViz = () => {
  const rootNode = useAppSelector(selectData);
  const nodeDataArray = nodeToArray(rootNode, null);
  console.log(nodeDataArray);

  return (
    <ReactDiagram
      initDiagram={initDiagram}
      divClassName={styles.diagramComponent}
      nodeDataArray={nodeDataArray}
    />
  );
};
