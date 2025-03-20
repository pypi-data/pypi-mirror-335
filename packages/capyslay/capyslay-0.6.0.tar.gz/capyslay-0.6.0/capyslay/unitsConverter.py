def unitsConverter():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout
            xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:padding="20dp"
            android:orientation="vertical">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Enter the value"
                android:textSize="20sp"
                android:textStyle="bold" />

            <EditText
                android:id="@+id/inputVal"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Enter value"
                android:inputType="numberDecimal" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="From"
                android:textSize="20sp" />

            <Spinner
                android:id="@+id/fromUnits"
                android:layout_width="match_parent"
                android:layout_height="wrap_content" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="To"
                android:textSize="20sp" />

            <Spinner
                android:id="@+id/toUnits"
                android:layout_width="match_parent"
                android:layout_height="wrap_content" />

            <Button
                android:id="@+id/btnConvert"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Convert" />

            <TextView
                android:id="@+id/display"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:textSize="30sp" />

        </LinearLayout>

        """,
        """
        package com.example.test;

        import android.os.Bundle;
        import android.view.View;
        import android.widget.*;
        import androidx.appcompat.app.AppCompatActivity;
        import java.util.HashMap;

        public class MainActivity extends AppCompatActivity implements View.OnClickListener {

            Spinner spinnerFrom, spinnerTo;
            Button btnConvert;
            TextView disp;
            EditText inpVal;
            HashMap<String, Double> dict = new HashMap<>();

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                // Initialize UI elements
                spinnerFrom = findViewById(R.id.fromUnits);
                spinnerTo = findViewById(R.id.toUnits);
                btnConvert = findViewById(R.id.btnConvert);
                disp = findViewById(R.id.display);
                inpVal = findViewById(R.id.inputVal);

                btnConvert.setOnClickListener(this);

                // Unit conversion values (all relative to meters)
                dict.put("km", 1000.0);
                dict.put("m", 1.0);
                dict.put("cm", 0.01);
                dict.put("mm", 0.001);

                // Populate the spinners with available units
                ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                        android.R.layout.simple_spinner_dropdown_item,
                        dict.keySet().toArray(new String[0]));

                spinnerFrom.setAdapter(adapter);
                spinnerTo.setAdapter(adapter);
            }

            @Override
            public void onClick(View v) {
                if (v == btnConvert) {
                    String num = inpVal.getText().toString().trim();
                    String fUnit = spinnerFrom.getSelectedItem().toString();
                    String tUnit = spinnerTo.getSelectedItem().toString();

                    if (num.isEmpty()) {
                        disp.setText("Enter a value");
                        return;
                    }

                    try {
                        double inputValue = Double.parseDouble(num);
                        double result = (inputValue * dict.get(fUnit)) / dict.get(tUnit);
                        disp.setText("Result: " + result + " " + tUnit);
                    } catch (NumberFormatException e) {
                        disp.setText("Invalid input");
                    } catch (Exception e) {
                        disp.setText("Conversion error");
                    }
                }
            }
        }

        """
    ]