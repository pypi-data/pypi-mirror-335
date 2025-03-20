def currencyConverter():
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
                android:hint="Enter value" />

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
            Button btn_convert;
            TextView disp;
            EditText inpVal;
            HashMap<String, Double> dict = new HashMap<>();

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                spinnerFrom = findViewById(R.id.fromUnits);
                spinnerTo = findViewById(R.id.toUnits);
                btn_convert = findViewById(R.id.btnConvert);
                disp = findViewById(R.id.display);
                inpVal = findViewById(R.id.inputVal);
                
                btn_convert.setOnClickListener(this);

                // Example exchange rates (1 unit of currency in terms of USD)
                dict.put("USD", 1.0);
                dict.put("EUR", 0.92);
                dict.put("INR", 83.0);
                dict.put("GBP", 0.78);
                dict.put("JPY", 150.0);

                // Populate the spinners with available currencies
                ArrayAdapter<String> adapter = new ArrayAdapter<>(this, 
                    android.R.layout.simple_spinner_dropdown_item, 
                    dict.keySet().toArray(new String[0]));

                spinnerFrom.setAdapter(adapter);
                spinnerTo.setAdapter(adapter);
            }

            @Override
            public void onClick(View v) {
                if (v == btn_convert) {
                    String num = inpVal.getText().toString();
                    String fUnit = spinnerFrom.getSelectedItem().toString();
                    String tUnit = spinnerTo.getSelectedItem().toString();

                    if (num.isEmpty()) {
                        disp.setText("Enter a value");
                        return;
                    }

                    try {
                        double ans = dict.get(fUnit) * Double.parseDouble(num) / dict.get(tUnit);
                        disp.setText("Converted Amount: " + ans + " " + tUnit);
                    } catch (Exception e) {
                        disp.setText("Invalid Conversion");
                    }
                }
            }
        }
        """
    ]