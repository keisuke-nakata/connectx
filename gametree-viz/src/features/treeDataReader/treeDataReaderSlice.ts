import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export interface TreeDataReaderState {
  data: object;
  status: 'idle' | 'loading' | 'failed';
}

const initialState: TreeDataReaderState = {
  data: {},
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
  return JSON.parse(reader.result as string);
}

export const readSingleFileAsync = createAsyncThunk(
  'treeDataReader/readFileFromInput',
  async (file: File) => {
    const result = await parseFile(file);
    return result
  }
);

export const treeDataReaderSlice = createSlice({
  name: 'treeDataReader',
  initialState,
  reducers: {
    setData: (state, action: PayloadAction<object>) => {
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
