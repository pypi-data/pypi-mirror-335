def database1():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout
            xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:gravity="center"
            android:orientation="vertical"
            android:padding="20dp">

            <EditText
                android:id="@+id/etName"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Enter Name"/>

            <EditText
                android:id="@+id/etRegNo"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Enter Reg No"/>

            <Button
                android:id="@+id/btnRegister"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Register"/>

            <Button
                android:id="@+id/btnView"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="View Stored Details"/>

        </LinearLayout>
        """,
        """
        package com.example.program10;

        import android.database.Cursor;
        import android.os.Bundle;
        import android.view.View;
        import android.widget.Button;
        import android.widget.EditText;
        import android.widget.Toast;
        import androidx.appcompat.app.AlertDialog;
        import androidx.appcompat.app.AppCompatActivity;

        public class MainActivity extends AppCompatActivity {

            private EditText etName, etRegNo;
            
            private Button btnRegister, btnView;
            private DatabaseHelper dbHelper;

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                etName = findViewById(R.id.etName);
                etRegNo = findViewById(R.id.etRegNo);
                btnRegister = findViewById(R.id.btnRegister);
                btnView = findViewById(R.id.btnView);

                dbHelper = new DatabaseHelper(this);

                btnRegister.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String name = etName.getText().toString();
                        String regNo = etRegNo.getText().toString();

                        if (name.isEmpty() || regNo.isEmpty()) {
                            Toast.makeText(MainActivity.this, "Please fill all fields", Toast.LENGTH_SHORT).show();
                        } else {
                            boolean isInserted = dbHelper.insertData(name, regNo);
                            if (isInserted) {
                                Toast.makeText(MainActivity.this, "Registered Successfully", Toast.LENGTH_SHORT).show();
                                etName.setText("");
                                etRegNo.setText("");
                            } else {
                                Toast.makeText(MainActivity.this, "Registration Failed", Toast.LENGTH_SHORT).show();
                            }
                        }
                    }
                });

                btnView.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        Cursor cursor = dbHelper.getAllData();
                        if (cursor.getCount() == 0) {
                            showMessage("Error", "No Data Found!");
                            return;
                        }

                        StringBuilder buffer = new StringBuilder();
                        while (cursor.moveToNext()) {
                            buffer.append("Name: ").append(cursor.getString(0)).append("\n");
                            buffer.append("Reg No: ").append(cursor.getString(1)).append("\n\n");
                        }
                        showMessage("Stored Details", buffer.toString());
                    }
                });
            }

            private void showMessage(String title, String message) {
                AlertDialog.Builder builder = new AlertDialog.Builder(this);
                builder.setTitle(title);
                builder.setMessage(message);
                builder.setPositiveButton("OK", null);
                builder.show();
            }
        }
        """,
        """DatabaseHelper.java""",
        """
        package com.example.program10;

        import android.content.ContentValues;
        import android.content.Context;
        import android.database.Cursor;
        import android.database.sqlite.SQLiteDatabase;
        import android.database.sqlite.SQLiteOpenHelper;

        public class DatabaseHelper extends SQLiteOpenHelper {

            private static final String DATABASE_NAME = "StudentDB";
            private static final String TABLE_NAME = "students";
            private static final String COL_NAME = "NAME";
            private static final String COL_REGNO = "REGNO";

            public DatabaseHelper(Context context) {
                super(context, DATABASE_NAME, null, 1);
            }

            public void onCreate(SQLiteDatabase db) {
                String createTable = "CREATE TABLE " + TABLE_NAME + " (" +
                        COL_NAME + " TEXT, " +
                        COL_REGNO + " TEXT)";
                db.execSQL(createTable);
            }

            public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
                db.execSQL("DROP TABLE IF EXISTS " + TABLE_NAME);
                onCreate(db);
            }

            public boolean insertData(String name, String regNo) {
                SQLiteDatabase db = this.getWritableDatabase();
                ContentValues values = new ContentValues();
                values.put(COL_NAME, name);
                values.put(COL_REGNO, regNo);

                long result = db.insert(TABLE_NAME, null, values);
                return result != -1; // Return true if inserted successfully
            }

            public Cursor getAllData() {
                SQLiteDatabase db = this.getReadableDatabase();
                return db.rawQuery("SELECT * FROM " + TABLE_NAME, null);
            }
        }
        """
    ]