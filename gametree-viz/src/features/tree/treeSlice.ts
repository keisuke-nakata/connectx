import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { Node } from './node';
import nodeTI from "./node-ti";
import { CheckerT, createCheckers } from "ts-interface-checker";
import { ChangeEvent } from 'react';

interface TreeState {
  data: Node;
  status: 'idle' | 'loading' | 'failed';
  readMsg: string;
}

const initialState: TreeState = {
  data: {
    id: "0",
    repr: "node 0",
    isTerminal: true,
    score: NaN,
    isRational: true,
    parentEdge: null,
    children: [],
  },
  status: 'idle',
  readMsg: '',
};

const nodeChecker = createCheckers(nodeTI) as { Node: CheckerT<Node> };

const readFile = (file: File) => {
  return new Promise<FileReader>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader);
    reader.onerror = (error) => reject(error);
    reader.readAsText(file);
  })
};

const parseFile = async (file: File) => {
  const reader = await readFile(file);
  const data = JSON.parse(reader.result as string);
  try {
    nodeChecker.Node.strictCheck(data);
  } catch (error) {
    throw error;
  }
  return data as Node;
};

export const readSingleFileAsync = createAsyncThunk(
  'tree/readFileFromInput',
  async (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) {
      throw Error('event.target.files is null');
    }
    const file = event.target.files[0];
    if (!file) {
      throw Error('file is null');
    }
    const rootNode = await parseFile(file) as Node;
    return rootNode;
  }
);

export const treeSlice = createSlice({
  name: 'tree',
  initialState,
  reducers: {
    setData: (state, action: PayloadAction<Node>) => {
      console.log(action.payload);
      state.data = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(readSingleFileAsync.pending, (state) => {
        state.status = 'loading';
        state.readMsg = 'loading';
      })
      .addCase(readSingleFileAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
        state.readMsg = '';
      })
      .addCase(readSingleFileAsync.rejected, (state, action) => {
        state.status = 'failed';
        state.data = initialState.data;
        const readMsg =
          (action.error.name ?? "UnknownError")
          + ": "
          + (action.error.message ?? "")
          + " "
          + (action.error.code ?? "");
        state.readMsg = readMsg;
      });
  },
});

export const { setData } = treeSlice.actions;

export const selectData = (state: RootState) => state.tree.data;
export const selectReadMsg = (state: RootState) => state.tree.readMsg;

export default treeSlice.reducer;
