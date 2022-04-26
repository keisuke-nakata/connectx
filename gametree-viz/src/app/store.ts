import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import counterReducer from '../features/counter/counterSlice';
import treeDataReaderRecuder from '../features/treeDataReader/treeDataReaderSlice';

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    treeDataReader: treeDataReaderRecuder,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
