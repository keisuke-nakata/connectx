import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { Node } from '../common/node';
import { parseNode } from '../common/parseNode';

export interface TreeDataReaderState {
  data: Node;
  status: 'idle' | 'loading' | 'failed';
}

const initialState: TreeDataReaderState = {
  data: {
    id: 0,
    repr: "node 0",
    isTerminal: true,
    score: null,
    property: {},
    parentEdge: null,
    children: [],
  },
  status: 'idle',
};


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
  return parseNode(JSON.parse(reader.result as string));
};

export const readSingleFileAsync = createAsyncThunk(
  'treeDataReader/readFileFromInput',
  async (file: File) => {
    const rootNode = await parseFile(file) as Node;
    return rootNode;
  }
);

export const treeDataReaderSlice = createSlice({
  name: 'treeDataReader',
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
      })
      .addCase(readSingleFileAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.data = action.payload;
      })
      .addCase(readSingleFileAsync.rejected, (state) => {
        state.status = 'failed';
      });
  },
});

export const { setData } = treeDataReaderSlice.actions;

export const selectData = (state: RootState) => state.treeDataReader.data;

export default treeDataReaderSlice.reducer;
